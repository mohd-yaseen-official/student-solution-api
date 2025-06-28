from django.db import models
from django.contrib.auth.models import User

from timetable.models import Subject


class Homework(models.Model):
    title = models.CharField(max_length=200)

    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_completed = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Homework"
        verbose_name_plural = "Homeworks"
        ordering = ['-due_date']


    def __str__(self):
        return self.title
