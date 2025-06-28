from django.urls import path

from .views import *


app_name = 'homeworks'

urlpatterns = [
    path('create/', create_homework),
    path('manage/', manage_homework),

]
