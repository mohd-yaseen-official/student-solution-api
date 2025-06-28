# views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from timetable.models import Timetable
from .serializers import TimetableCreateSerializer, TimetableManageSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_timetable(request):
    """
    Create a new timetable for the authenticated user
    """
    serializer = TimetableCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        timetable = serializer.save()
        # Return the created timetable with full details
        response_serializer = TimetableManageSerializer(timetable)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_timetable(request):
    """
    GET: Return the first timetable of the currently logged in user
    PUT: Update the user's timetable
    DELETE: Delete the user's timetable
    """
    try:
        # Get the first timetable of the current user
        timetable = Timetable.objects.filter(user=request.user).first()
        if not timetable:
            return Response({'error': 'No timetable found for this user'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'GET':
            serializer = TimetableManageSerializer(timetable)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = TimetableManageSerializer(timetable, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            timetable.delete()
            return Response({'message': 'Timetable deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)