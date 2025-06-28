from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from homeworks.models import Homework
from .serializers import HomeworkSerializer


@api_view([ 'POST'])
@permission_classes([IsAuthenticated])
def create_homework(request):
    serializer = HomeworkSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            'status': 201,
            'message': 'Homework created successfully.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response({
        'status': 400,
        'message': 'Validation error.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_homework(request):
    user = request.user

    if request.method == 'GET':
        due_date = request.query_params.get('due_date')
        is_completed = request.query_params.get('is_completed')

        homeworks = Homework.objects.filter(user=user, is_deleted=False)

        if due_date:
            homeworks = homeworks.filter(due_date=due_date)

        if is_completed is not None:
            if is_completed.lower() == 'true':
                homeworks = homeworks.filter(is_completed=True)
            elif is_completed.lower() == 'false':
                homeworks = homeworks.filter(is_completed=False)

        homeworks = homeworks.order_by('created_at')
        serializer = HomeworkSerializer(homeworks, many=True)

        return Response({
            'status': 200,
            'message': 'Homeworks fetched successfully.',
            'data': serializer.data
    }, status=status.HTTP_200_OK)

    
    elif request.method == 'DELETE':
        homework_id = request.data.get('id')
        if not homework_id:
            return Response({
                'status': 400,
                'message': 'Homework ID is required.',
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            homework = Homework.objects.get(id=homework_id, user=user, is_deleted=False)
            homework.is_deleted = True
            homework.save()
            return Response({
                'status': 200,
                'message': 'Homework deleted successfully.',
                'data': {'id': homework_id}
            }, status=status.HTTP_200_OK)
        except Homework.DoesNotExist:
            return Response({
                'status': 404,
                'message': 'Homework not found.',
            }, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'PUT':
        homework_id = request.data.get('id')

        if not homework_id:
            return Response({
                'status': 400,
                'message': 'Homework ID is required.',
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            homework = Homework.objects.get(id=homework_id, user=user, is_deleted=False)
        except Homework.DoesNotExist:
            return Response({
                'status': 404,
                'message': 'Homework not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        homework.is_completed = True
        homework.save()

        serializer = HomeworkSerializer(homework)

        return Response({
            'status': 200,
            'message': 'Homework marked as completed.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)