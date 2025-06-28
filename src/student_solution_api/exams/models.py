from django.db import models
from django.contrib.auth.models import User
from timetable.models import Subject

class Exam(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exams')
    subjects = models.ManyToManyField(Subject, through='ExamSubject', related_name='exams')

    def __str__(self):
        return self.title

    @property
    def progress(self):
        exam_subjects = self.exam_subjects.all()
        if not exam_subjects.exists():
            return 0
        total_progress = sum(subject.progress for subject in exam_subjects)
        return round(total_progress / exam_subjects.count())


class ExamSubject(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exam_subjects')
    chapters = models.ManyToManyField('Chapter', through='ExamChapter', related_name='exam_subjects')

    class Meta:
        unique_together = ('exam', 'subject')

    def __str__(self):
        return f"{self.exam.title} - {self.subject.name}"

    @property
    def progress(self):
        completed_chapters = self.exam_chapters.filter(is_completed=True).count()
        total_chapters = self.exam_chapters.count()
        if total_chapters == 0:
            return 0
        return round((completed_chapters / total_chapters) * 100)


class Chapter(models.Model):
    title = models.CharField(max_length=200)
    chapter_number = models.PositiveIntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='chapters')

    def __str__(self):
        return f"{self.chapter_number}. {self.title}"


class ExamChapter(models.Model):
    exam_subject = models.ForeignKey(ExamSubject, on_delete=models.CASCADE, related_name='exam_chapters')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='exam_chapters')
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('exam_subject', 'chapter')

    def __str__(self):
        return f"{self.exam_subject} - {self.chapter.title}"
