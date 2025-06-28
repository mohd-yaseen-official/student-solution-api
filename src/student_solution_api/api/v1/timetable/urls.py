from django.urls import path

from .views import *


app_name = 'timetable'

urlpatterns = [
    path('create/', create_timetable, name='create-timetable'),
    path('manage/', manage_timetable, name='manage-timetable'),
]
