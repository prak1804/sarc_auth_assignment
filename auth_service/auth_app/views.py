from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CentralUser
from .serializers import RegisterSerializer, LoginSerializer, UserDetailSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    # Embed extra claims in token
    refresh['roll_number'] = user.roll_number
    refresh['name'] = user.name
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user.
    Accepts: username, name, roll_number, hostel_number, password
    This is the ONLY endpoint that accepts and hashes passwords.
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response(
            {
                'message': 'User registered successfully.',
                'user': UserDetailSerializer(user).data,
                'tokens': tokens,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login with username and password.
    Returns JWT access + refresh tokens.
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response(
            {'error': 'Invalid username or password.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_active:
        return Response(
            {'error': 'This account has been deactivated.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    tokens = get_tokens_for_user(user)
    return Response(
        {
            'message': 'Login successful.',
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': UserDetailSerializer(user).data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_token(request):
    """
    Service-to-service token verification endpoint.
    Called by independent websites to validate a user's JWT token.
    Returns verified identity details if token is valid.
    """
    token_str = request.data.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token_str:
        return Response({'error': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

        token = AccessToken(token_str)
        user_id = token['user_id']

        user = CentralUser.objects.get(id=user_id, is_active=True)

        return Response(
            {
                'valid': True,
                'user': UserDetailSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
    except CentralUser.DoesNotExist:
        return Response({'valid': False, 'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'valid': False, 'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """Refresh access token using refresh token."""
    from rest_framework_simplejwt.tokens import RefreshToken
    from rest_framework_simplejwt.exceptions import TokenError

    refresh_str = request.data.get('refresh')
    if not refresh_str:
        return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        refresh = RefreshToken(refresh_str)
        return Response(
            {'access': str(refresh.access_token)},
            status=status.HTTP_200_OK,
        )
    except TokenError as e:
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Get current user's details (requires valid JWT)."""
    return Response(UserDetailSerializer(request.user).data)
