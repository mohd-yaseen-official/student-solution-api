# urls.py
from django.urls import path
from . import views

app_name = 'exams'
urlpatterns = [
    # Create exam
    path('create/', views.create_exam, name='create_exam'),
    
    # View all exams (list)
    path('view/', views.view_exams, name='view_exams'),
    
    # Manage specific exam (view, patch update, delete, manage chapters)
    path('manage/<int:id>/', views.manage_exam, name='manage_exam'),
]