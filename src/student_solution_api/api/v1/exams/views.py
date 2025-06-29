from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from exams.models import Exam, ExamChapter
from .serializers import (
    ExamSerializer, 
    ExamListSerializer,
    ExamUpdateSerializer,
    UpdateChapterStatusSerializer, 
    BulkUpdateChapterStatusSerializer
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_exam(request):
    """
    Create a new exam with subjects and chapters
    POST /create/
    """
    serializer = ExamSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        exam = serializer.save()
        response_data = ExamSerializer(exam, context={'request': request}).data
        
        return Response({
            'status': 201,
            'message': 'Exam created successfully.',
            'data': response_data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'status': 400,
        'message': 'Validation error.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_exams(request):
    """
    List all exams for the authenticated user
    GET /view/
    """
    exams = Exam.objects.filter(user=request.user).order_by('-id')
    serializer = ExamListSerializer(exams, many=True, context={'request': request})
    
    return Response({
        'status': 200,
        'message': 'Exams retrieved successfully.',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_exam(request, id):
    """
    Manage a specific exam: view, update, delete, and manage chapters
    
    GET /manage/<id>/ - Get exam details
    PATCH /manage/<id>/ - Update exam or chapter status based on payload:
        - Update exam title: {"title": "New Title"}
        - Add subjects/chapters: {"subjects": [...]}
        - Update single chapter: {"chapter_id": 1, "is_completed": true}
        - Bulk update chapters: {"chapters": [{"chapter_id": 1, "is_completed": true}, ...]}
        - Get stats: {"action": "stats"}
    DELETE /manage/<id>/ - Delete exam
    """
    
    # Get the exam (with user ownership check)
    exam = get_object_or_404(Exam, id=id, user=request.user)
    
    # Handle exam details retrieval
    if request.method == 'GET':
        serializer = ExamSerializer(exam, context={'request': request})
        return Response({
            'status': 200,
            'message': 'Exam retrieved successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    # Handle exam updates (title, subjects, chapters)
    elif request.method == 'PATCH':
        # Check if this is a stats request
        if request.data.get('action') == 'stats':
            return get_exam_stats(exam)
        
        # Check if this is a bulk chapter update
        if 'chapters' in request.data:
            return bulk_update_chapters_status(exam, request.data)
        
        # Check if this is a single chapter update
        if 'chapter_id' in request.data:
            return update_single_chapter_status(exam, request.data)
        
        # Otherwise, it's an exam structure update (title and/or subjects)
        return update_exam_structure(exam, request.data)
    
    # Handle exam deletion
    elif request.method == 'DELETE':
        exam_title = exam.title
        exam.delete()
        return Response({
            'status': 200,
            'message': f'Exam "{exam_title}" deleted successfully.'
        }, status=status.HTTP_200_OK)


def update_exam_structure(exam, data):
    """Helper function to update exam title and/or add subjects/chapters"""
    serializer = ExamUpdateSerializer(exam, data=data, partial=True)
    
    if serializer.is_valid():
        try:
            exam = serializer.save()
            response_data = ExamSerializer(exam).data
            
            return Response({
                'status': 200,
                'message': 'Exam updated successfully.',
                'data': response_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 400,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'status': 400,
        'message': 'Validation error.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


def update_single_chapter_status(exam, data):
    """Helper function to update single chapter status"""
    serializer = UpdateChapterStatusSerializer(data=data)
    
    if serializer.is_valid():
        try:
            serializer.update_chapter_status(exam, serializer.validated_data)
            
            # Return updated exam data
            exam_serializer = ExamSerializer(exam)
            
            return Response({
                'status': 200,
                'message': 'Chapter status updated successfully.',
                'data': exam_serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 400,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'status': 400,
        'message': 'Validation error.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


def bulk_update_chapters_status(exam, data):
    """Helper function to bulk update chapters status"""
    serializer = BulkUpdateChapterStatusSerializer(data=data)
    
    if serializer.is_valid():
        try:
            updated_chapters = serializer.update_chapters_status(exam, serializer.validated_data)
            
            # Return updated exam data
            exam_serializer = ExamSerializer(exam)
            
            return Response({
                'status': 200,
                'message': f'{len(updated_chapters)} chapters updated successfully.',
                'data': exam_serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 400,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'status': 400,
        'message': 'Validation error.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


def get_exam_stats(exam):
    """Helper function to get exam statistics"""
    total_chapters = exam.exam_chapters.count()
    completed_chapters = exam.exam_chapters.filter(is_completed=True).count()
    
    # Get subject-wise stats
    subjects_stats = []
    for subject in exam.subjects.all():
        subject_total = exam.exam_chapters.filter(chapter__subject=subject).count()
        subject_completed = exam.exam_chapters.filter(
            chapter__subject=subject, 
            is_completed=True
        ).count()
        subject_progress = round((subject_completed / subject_total) * 100) if subject_total else 0
        
        subjects_stats.append({
            'id': subject.id,
            'subject_name': subject.name,
            'total_chapters': subject_total,
            'completed_chapters': subject_completed,
            'progress': subject_progress
        })
    
    stats = {
        'exam_id': exam.id,
        'exam_title': exam.title,
        'overall_progress': exam.progress,
        'total_chapters': total_chapters,
        'completed_chapters': completed_chapters,
        'pending_chapters': total_chapters - completed_chapters,
        'subjects_count': exam.subjects.count(),
        'subjects_stats': subjects_stats
    }
    
    return Response({
        'status': 200,
        'message': 'Exam stats retrieved successfully.',
        'data': stats
    }, status=status.HTTP_200_OK)