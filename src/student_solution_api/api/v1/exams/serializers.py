from rest_framework import serializers
from exams.models import Exam, ExamSubject, Chapter, ExamChapter
from timetable.models import Subject

class ChapterBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'chapter_number']

class ExamChapterSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='chapter.id', read_only=True)
    title = serializers.CharField(source='chapter.title', read_only=True)
    chapter_number = serializers.IntegerField(source='chapter.chapter_number', read_only=True)
    # For input
    is_completed = serializers.BooleanField(required=False)
    chapter = serializers.PrimaryKeyRelatedField(queryset=Chapter.objects.all(), required=False, write_only=True)

    class Meta:
        model = ExamChapter
        fields = ['id', 'title', 'chapter_number', 'is_completed', 'chapter']

class ExamSubjectSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='subject.name', read_only=True)
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), required=False, write_only=True)
    progress = serializers.SerializerMethodField(read_only=True)
    chapters = ExamChapterSerializer(many=True, required=False)

    class Meta:
        model = ExamSubject
        fields = ['name', 'subject', 'progress', 'chapters']

    def get_progress(self, obj):
        completed = obj.exam_chapters.filter(is_completed=True).count()
        total = obj.exam_chapters.count()
        return round((completed / total) * 100) if total else 0

class ExamSerializer(serializers.ModelSerializer):
    progress = serializers.IntegerField(read_only=True)
    subjects = ExamSubjectSerializer(many=True)

    class Meta:
        model = Exam
        fields = ['id', 'title', 'progress', 'subjects']

    def create(self, validated_data):
        subjects_data = validated_data.pop('subjects', [])
        user = self.context['request'].user
        exam = Exam.objects.create(title=validated_data['title'], user=user)
        for subj_data in subjects_data:
            # Get or create subject
            subject = subj_data.get('subject')
            if not subject:
                # Try to get by name if provided
                name = subj_data.get('name')
                subject, _ = Subject.objects.get_or_create(name=name)
            exam_subject = ExamSubject.objects.create(exam=exam, subject=subject)
            chapters_data = subj_data.get('chapters', [])
            for chap_data in chapters_data:
                # Get or create chapter
                chapter = chap_data.get('chapter')
                if not chapter:
                    chapter, _ = Chapter.objects.get_or_create(
                        title=chap_data.get('title'),
                        chapter_number=chap_data.get('chapter_number'),
                        subject=subject
                    )
                ExamChapter.objects.create(
                    exam_subject=exam_subject,
                    chapter=chapter,
                    is_completed=chap_data.get('is_completed', False)
                )
        return exam
