from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Day(models.Model):
    WEEKDAYS = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    name = models.CharField(max_length=20, choices=WEEKDAYS, unique=True)
    
    def __str__(self):
        return self.get_name_display()
    
    class Meta:
        ordering = ['id']

class Timetable(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timetables')
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    class Meta:
        ordering = ['name']

class Period(models.Model):
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='periods')
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    order = models.IntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.timetable.name} - {self.day.name} - Period {self.order}: {self.subject.name}"
    
    class Meta:
        ordering = ['day__id', 'order']
        unique_together = ['timetable', 'day', 'order']