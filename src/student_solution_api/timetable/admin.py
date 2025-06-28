from django.contrib import admin
from .models import Subject, Day, Period, Timetable


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    ordering = ['id']


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ['id', 'timetable', 'day', 'order', 'subject']
    list_filter = ['day', 'timetable']
    search_fields = ['subject__name']
    ordering = ['timetable', 'day__id', 'order']


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'user']
    ordering = ['name']
