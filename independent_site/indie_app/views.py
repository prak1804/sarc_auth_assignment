"""
Views for the Independent Website.

Key rules enforced here:
- Passwords are NEVER accepted, stored, or returned
- JWT tokens are NEVER generated here
- All authentication happens via the CentralAuthBackend (authentication.py)
- Registration is forwarded to the Centralized Auth Service
"""
import requests
from django.conf import settings
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import UserProfile
from .serializers import (
    UserProfileSerializer,
    RegisterForwardSerializer,
)


# ─── Registration (forwarded to Centralized Auth Service) ───────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Registration endpoint on the Independent Website.

    Flow:
    1. Collect user data (including password) from frontend
    2. Forward only required auth fields to Centralized Auth Service
    3. Centralized service hashes password and stores the user
    4. We create a local profile WITHOUT the password
    5. Return tokens received from centralized service
    """
    serializer = RegisterForwardSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    # Fields to forward to centralized auth service (includes password)
    auth_payload = {
        'username': data['username'],
        'name': data['name'],
        'roll_number': data['roll_number'],
        'hostel_number': data['hostel_number'],
        'password': data['password'],  # forwarded but never stored here
    }

    # Forward to Centralized Auth Service
    register_url = f"{settings.CENTRAL_AUTH_SERVICE_URL}/api/auth/register/"
    try:
        central_response = requests.post(register_url, json=auth_payload, timeout=5)
    except requests.exceptions.ConnectionError:
        return Response(
            {'error': 'Cannot reach authentication service.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except requests.exceptions.Timeout:
        return Response(
            {'error': 'Authentication service timed out.'},
            status=status.HTTP_504_GATEWAY_TIMEOUT,
        )

    if central_response.status_code != 201:
        # Forward the error from the centralized service
        return Response(central_response.json(), status=central_response.status_code)

    central_data = central_response.json()
    central_user = central_data['user']

    # Create local profile — NO password stored
    profile, _ = UserProfile.objects.get_or_create(
        roll_number=central_user['roll_number'],
        defaults={
            'central_user_id': central_user['id'],
            'username': central_user['username'],
            'name': central_user['name'],
            'department': data.get('department', ''),
            'year_of_study': data.get('year_of_study'),
        },
    )

    return Response(
        {
            'message': 'Registration successful.',
            'user': UserProfileSerializer(profile).data,
            'tokens': central_data.get('tokens', {}),
        },
        status=status.HTTP_201_CREATED,
    )


# ─── Dashboard ──────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """
    Dashboard endpoint — returns basic user data only.
    This requires a valid JWT from the centralized auth service.
    """
    user = request.user
    return Response({
        'user': UserProfileSerializer(user).data,
    })
