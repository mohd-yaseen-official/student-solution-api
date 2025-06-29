from django.db import models
from django.contrib.auth.models import User
from timetable.models import Subject

class Exam(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exams')
    subjects = models.ManyToManyField(Subject, related_name='exams', blank=True)
    chapters = models.ManyToManyField('Chapter', through='ExamChapter', related_name='exams')

    def __str__(self):
        return self.title

    @property
    def progress(self):
        exam_chapters = self.exam_chapters.all()
        if not exam_chapters.exists():
            return 0
        completed = exam_chapters.filter(is_completed=True).count()
        total = exam_chapters.count()
        return round((completed / total) * 100)

    def get_subject_progress(self, subject):
        """Get progress for a specific subject"""
        subject_chapters = self.exam_chapters.filter(chapter__subject=subject)
        if not subject_chapters.exists():
            return 0
        completed = subject_chapters.filter(is_completed=True).count()
        total = subject_chapters.count()
        return round((completed / total) * 100)


class Chapter(models.Model):
    title = models.CharField(max_length=200)
    chapter_number = models.PositiveIntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='chapters')

    class Meta:
        unique_together = ('title', 'chapter_number', 'subject')
        ordering = ['subject', 'chapter_number']

    def __str__(self):
        return f"{self.subject.name} - {self.chapter_number}. {self.title}"


class ExamChapter(models.Model):
    """Junction table for Exam and Chapter with completion status"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_chapters')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='exam_chapters')
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('exam', 'chapter')

    def __str__(self):
        return f"{self.exam.title} - {self.chapter.title}"