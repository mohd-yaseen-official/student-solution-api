from django.contrib import admin
from .models import Exam, Chapter, ExamChapter


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'chapter_number', 'subject']
    list_filter = ['subject']
    search_fields = ['title', 'subject__name']
    ordering = ['subject__name', 'chapter_number']
    list_per_page = 20


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'progress', 'subjects_count']
    list_filter = ['user']
    search_fields = ['title', 'user__username']
    ordering = ['-id']
    list_per_page = 20
    
    def subjects_count(self, obj):
        return obj.subjects.count()
    subjects_count.short_description = 'Subjects Count'


@admin.register(ExamChapter)
class ExamChapterAdmin(admin.ModelAdmin):
    list_display = ['id', 'exam', 'chapter', 'is_completed', 'created_at']
    list_filter = ['is_completed', 'exam', 'chapter__subject']
    search_fields = ['chapter__title', 'exam__title', 'chapter__subject__name']
    ordering = ['exam__title', 'chapter__subject__name', 'chapter__chapter_number']
    list_per_page = 20
    readonly_fields = ['created_at', 'updated_at']
