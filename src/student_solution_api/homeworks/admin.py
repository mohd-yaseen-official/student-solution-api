from django.contrib import admin

from .models import Homework


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'due_date', 'is_completed', 'is_deleted', 'created_at')
    list_filter = ('is_completed', 'is_deleted', 'subject')
    search_fields = ('title',)
    ordering = ('-due_date',)
