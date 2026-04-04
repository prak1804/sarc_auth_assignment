from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import UserProfile


def make_mock_profile():
    """Helper: create a UserProfile for testing (no password)."""
    return UserProfile.objects.create(
        central_user_id=1,
        username='testuser',
        name='Test User',
        roll_number='23CS001',
    )


def mock_verify_success(token):
    """Simulate successful token verification from centralized auth service."""
    return {
        'id': 1,
        'username': 'testuser',
        'name': 'Test User',
        'roll_number': '23CS001',
        'hostel_number': 'H7',
    }


class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.profile = make_mock_profile()

    def test_unauthenticated_request_rejected(self):
        res = self.client.get(reverse('dashboard'))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    @patch('indie_app.authentication.CentralAuthBackend._verify_token_with_central_service', side_effect=mock_verify_success)
    def test_authenticated_request_succeeds(self, mock_verify):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer fake.jwt.token')
        res = self.client.get(reverse('dashboard'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_no_password_field_in_userprofile(self):
        """UserProfile must not have a password field."""
        self.assertFalse(hasattr(UserProfile, 'password'))

    def test_no_password_stored_in_db(self):
        """Confirm UserProfile table has no password column."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='user_profiles'")
            columns = [row[0] for row in cursor.fetchall()]
        self.assertNotIn('password', columns)


class RegistrationForwardTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('indie-register')

    @patch('indie_app.views.requests.post')
    def test_registration_forwarded_to_central_service(self, mock_post):
        """Registration must forward credentials to centralized auth and never store password."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'user': {'id': 5, 'username': 'newuser', 'name': 'New User', 'roll_number': '23CS099'},
            'tokens': {'access': 'mock.access.token', 'refresh': 'mock.refresh.token'},
        }
        mock_post.return_value = mock_response

        payload = {
            'username': 'newuser',
            'name': 'New User',
            'roll_number': '23CS099',
            'hostel_number': 'H9',
            'password': 'secret1234',
            'department': 'CS',
        }
        res = self.client.post(self.register_url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # Verify the call was made to the central auth service
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        forwarded = call_args[1].get('json') or call_args[0][1]
        # Password was forwarded but must never be in local DB
        self.assertIn('password', forwarded)
        # Local profile must exist without password
        profile = UserProfile.objects.get(roll_number='23CS099')
        self.assertFalse(hasattr(profile, 'password'))

    @patch('indie_app.views.requests.post')
    def test_central_service_error_propagated(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'username': ['This field already exists.']}
        mock_post.return_value = mock_response

        res = self.client.post(self.register_url, {
            'username': 'dup', 'name': 'Dup', 'roll_number': '23CS000',
            'hostel_number': 'H1', 'password': 'pass1234',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


