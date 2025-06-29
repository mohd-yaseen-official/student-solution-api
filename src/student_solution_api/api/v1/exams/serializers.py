from rest_framework import serializers
from exams.models import Exam, Chapter, ExamChapter
from timetable.models import Subject
from collections import defaultdict

class ChapterSerializer(serializers.ModelSerializer):
    is_completed = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Chapter
        fields = ['id', 'title', 'chapter_number', 'is_completed']


class SubjectSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    progress = serializers.IntegerField(read_only=True)
    chapters = ChapterSerializer(many=True)

    class Meta:
        model = Subject
        fields = ['id', 'name', 'progress', 'chapters']


class ExamListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing exams"""
    progress = serializers.SerializerMethodField(read_only=True)
    subjects_count = serializers.SerializerMethodField(read_only=True)
    total_chapters = serializers.SerializerMethodField(read_only=True)
    completed_chapters = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Exam
        fields = [
            'id', 'title', 'progress', 'subjects_count', 
            'total_chapters', 'completed_chapters'
        ]

    def get_progress(self, obj):
        return obj.progress

    def get_subjects_count(self, obj):
        return obj.subjects.count()

    def get_total_chapters(self, obj):
        return obj.exam_chapters.count()

    def get_completed_chapters(self, obj):
        return obj.exam_chapters.filter(is_completed=True).count()


class ExamSerializer(serializers.ModelSerializer):
    """Detailed serializer for creating/viewing exams"""
    progress = serializers.SerializerMethodField(read_only=True)
    subjects = SubjectSerializer(many=True)

    class Meta:
        model = Exam
        fields = ['id', 'title', 'progress', 'subjects']

    def get_progress(self, obj):
        return obj.progress

    def to_representation(self, instance):
        """Custom representation to group chapters by subject"""
        data = super().to_representation(instance)
        
        # Group chapters by subject
        subjects_data = []
        exam_chapters = instance.exam_chapters.select_related('chapter', 'chapter__subject').all()
        
        # Group by subject
        subjects_dict = defaultdict(list)
        for exam_chapter in exam_chapters:
            subject = exam_chapter.chapter.subject
            chapter_data = {
                'id': exam_chapter.chapter.id,
                'title': exam_chapter.chapter.title,
                'chapter_number': exam_chapter.chapter.chapter_number,
                'is_completed': exam_chapter.is_completed
            }
            subjects_dict[subject].append(chapter_data)
        
        # Build subjects list
        for subject, chapters in subjects_dict.items():
            # Calculate progress for this subject
            completed = sum(1 for ch in chapters if ch['is_completed'])
            total = len(chapters)
            progress = round((completed / total) * 100) if total else 0
            
            # Sort chapters by chapter_number
            chapters.sort(key=lambda x: x['chapter_number'])
            
            subject_data = {
                'id': subject.id,
                'name': subject.name,
                'progress': progress,
                'chapters': chapters
            }
            subjects_data.append(subject_data)
        
        # Sort subjects by name
        subjects_data.sort(key=lambda x: x['name'])
        data['subjects'] = subjects_data
        
        return data

    def create(self, validated_data):
        subjects_data = validated_data.pop('subjects', [])
        user = self.context['request'].user
        
        # Create the exam
        exam = Exam.objects.create(
            title=validated_data['title'], 
            user=user
        )
        
        # Process subjects and chapters
        subjects_to_add = []
        
        for subject_data in subjects_data:
            subject_name = subject_data.get('name')
            if not subject_name:
                continue
                
            # Get or create subject
            subject, _ = Subject.objects.get_or_create(name=subject_name)
            subjects_to_add.append(subject)
            
            # Process chapters for this subject
            chapters_data = subject_data.get('chapters', [])
            for chapter_data in chapters_data:
                title = chapter_data.get('title')
                chapter_number = chapter_data.get('chapter_number')
                is_completed = chapter_data.get('is_completed', False)
                
                if title and chapter_number is not None:
                    # Get or create chapter
                    chapter, _ = Chapter.objects.get_or_create(
                        title=title,
                        chapter_number=chapter_number,
                        subject=subject
                    )
                    
                    # Create ExamChapter (junction record)
                    ExamChapter.objects.create(
                        exam=exam,
                        chapter=chapter,
                        is_completed=is_completed
                    )
        
        # Add subjects to exam
        if subjects_to_add:
            exam.subjects.set(subjects_to_add)
        
        return exam


class ExamUpdateSerializer(serializers.ModelSerializer):
    """Serializer for PATCH updates to exam structure (title and/or subjects)"""
    subjects = SubjectSerializer(many=True, required=False)

    class Meta:
        model = Exam
        fields = ['title', 'subjects']

    def update(self, instance, validated_data):
        # Update exam title if provided
        if 'title' in validated_data:
            instance.title = validated_data['title']
            instance.save()
        
        # Handle subjects update if provided
        subjects_data = validated_data.get('subjects', [])
        if subjects_data:
            # Instead of replacing all, we'll add new subjects and chapters
            existing_subjects = set(instance.subjects.all())
            subjects_to_add = []
            
            for subject_data in subjects_data:
                subject_name = subject_data.get('name')
                if not subject_name:
                    continue
                    
                subject, _ = Subject.objects.get_or_create(name=subject_name)
                subjects_to_add.append(subject)
                
                # Add new chapters for this subject (don't remove existing ones)
                chapters_data = subject_data.get('chapters', [])
                for chapter_data in chapters_data:
                    title = chapter_data.get('title')
                    chapter_number = chapter_data.get('chapter_number')
                    is_completed = chapter_data.get('is_completed', False)
                    
                    if title and chapter_number is not None:
                        chapter, _ = Chapter.objects.get_or_create(
                            title=title,
                            chapter_number=chapter_number,
                            subject=subject
                        )
                        
                        # Only create ExamChapter if it doesn't exist
                        exam_chapter, created = ExamChapter.objects.get_or_create(
                            exam=instance,
                            chapter=chapter,
                            defaults={'is_completed': is_completed}
                        )
                        
                        # If it already exists, optionally update completion status
                        if not created and 'is_completed' in chapter_data:
                            exam_chapter.is_completed = is_completed
                            exam_chapter.save()
            
            # Add new subjects to the exam (keeps existing ones)
            if subjects_to_add:
                all_subjects = existing_subjects.union(set(subjects_to_add))
                instance.subjects.set(all_subjects)
        
        return instance


class UpdateChapterStatusSerializer(serializers.Serializer):
    """Serializer for updating individual chapter completion status"""
    chapter_id = serializers.IntegerField()
    is_completed = serializers.BooleanField()

    def update_chapter_status(self, exam, validated_data):
        chapter_id = validated_data['chapter_id']
        is_completed = validated_data['is_completed']
        
        try:
            exam_chapter = ExamChapter.objects.get(
                exam=exam,
                chapter_id=chapter_id
            )
            exam_chapter.is_completed = is_completed
            exam_chapter.save()
            return exam_chapter
        except ExamChapter.DoesNotExist:
            raise serializers.ValidationError("Chapter not found in this exam.")


class BulkUpdateChapterStatusSerializer(serializers.Serializer):
    """Serializer for bulk updating chapter completion status"""
    chapters = UpdateChapterStatusSerializer(many=True)

    def update_chapters_status(self, exam, validated_data):
        chapters_data = validated_data['chapters']
        updated_chapters = []
        errors = []
        
        for chapter_data in chapters_data:
            try:
                chapter_id = chapter_data['chapter_id']
                is_completed = chapter_data['is_completed']
                
                exam_chapter = ExamChapter.objects.get(
                    exam=exam,
                    chapter_id=chapter_id
                )
                exam_chapter.is_completed = is_completed
                exam_chapter.save()
                updated_chapters.append(exam_chapter)
                
            except ExamChapter.DoesNotExist:
                errors.append(f"Chapter {chapter_data.get('chapter_id')} not found in this exam")
                continue
        
        if errors and not updated_chapters:
            raise serializers.ValidationError(errors)
        
        return updated_chapters