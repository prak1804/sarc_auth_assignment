"""
Custom DRF authentication backend for the Independent Website.

This backend:
- Reads the Bearer token from the Authorization header
- Calls the Centralized Auth Service's /api/auth/verify/ endpoint
- If valid, returns a local UserProfile (creating one if it's the first login)
- NEVER handles passwords or generates tokens
"""
import requests
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import UserProfile


class CentralAuthBackend(BaseAuthentication):
    """
    Authenticates requests by forwarding the JWT token to the
    Centralized Authentication Service for verification.
    """

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return None  # Let other auth backends handle it

        token = auth_header.split(' ', 1)[1].strip()

        if not token:
            return None

        # Call centralized auth service to verify the token
        identity = self._verify_token_with_central_service(token)

        # Get or create local profile (no password stored here)
        user_profile = self._get_or_create_local_profile(identity)

        return (user_profile, token)

    def _verify_token_with_central_service(self, token):
        """Make a service-to-service call to the centralized auth service."""
        verify_url = f"{settings.CENTRAL_AUTH_SERVICE_URL}/api/auth/verify/"
        try:
            response = requests.post(
                verify_url,
                json={'token': token},
                timeout=5,
            )
        except requests.exceptions.ConnectionError:
            raise AuthenticationFailed('Cannot reach authentication service.')
        except requests.exceptions.Timeout:
            raise AuthenticationFailed('Authentication service timed out.')

        if response.status_code == 200:
            data = response.json()
            if data.get('valid'):
                return data['user']
            raise AuthenticationFailed(data.get('error', 'Token invalid.'))

        raise AuthenticationFailed('Token verification failed.')

    def _get_or_create_local_profile(self, identity):
        """
        Get existing local profile or create a new one on first login.
        No password is stored here — only identity info from centralized service.
        """
        roll_number = identity['roll_number']
        profile, created = UserProfile.objects.get_or_create(
            roll_number=roll_number,
            defaults={
                'username': identity['username'],
                'name': identity['name'],
                'central_user_id': identity['id'],
            },
        )

        if not created:
            # Update cached identity fields in case they changed
            profile.username = identity['username']
            profile.name = identity['name']
            profile.save(update_fields=['username', 'name'])

        return profile

    def authenticate_header(self, request):
        return 'Bearer'
