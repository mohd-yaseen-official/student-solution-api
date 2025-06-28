from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from .serializers import UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        refresh_token = RefreshToken.for_user(user)
        token = {
            'refresh': str(refresh_token),
            'access': str(refresh_token.access_token)
        }

        return Response({
            'status': 201,
            'message': 'User created successfully.',
            'token': token
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'status': 400,
        'message': 'Validation error',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_user(request):
    user = request.user

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response({
            'status': 200,
            'message': 'User fetched successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 200,
                'message': 'User updated successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 400,
            'message': 'Validation error.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.is_active = False
        user.save()
        
        return Response({
            'status': 204,
            'message': 'User deleted successfully.'
        }, status=status.HTTP_204_NO_CONTENT)