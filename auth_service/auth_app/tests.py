from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import CentralUser


class RegistrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.valid_payload = {
            'username': 'testuser',
            'name': 'Test User',
            'roll_number': '23CS001',
            'hostel_number': 'H7',
            'password': 'securepass123',
        }

    def test_register_success(self):
        res = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', res.data)
        self.assertIn('access', res.data['tokens'])
        self.assertEqual(res.data['user']['roll_number'], '23CS001')

    def test_register_duplicate_username(self):
        self.client.post(self.register_url, self.valid_payload, format='json')
        res = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_roll_number(self):
        self.client.post(self.register_url, self.valid_payload, format='json')
        payload2 = {**self.valid_payload, 'username': 'otheruser'}
        res = self.client.post(self.register_url, payload2, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        res = self.client.post(self.register_url, {'username': 'only'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_hashed(self):
        """Passwords must never be stored in plaintext."""
        self.client.post(self.register_url, self.valid_payload, format='json')
        user = CentralUser.objects.get(username='testuser')
        self.assertNotEqual(user.password, 'securepass123')
        self.assertTrue(user.password.startswith('pbkdf2') or user.password.startswith('bcrypt') or '$' in user.password)


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        self.user = CentralUser.objects.create_user(
            username='loginuser',
            name='Login User',
            roll_number='23CS002',
            hostel_number='H3',
            password='testpass456',
        )

    def test_login_success(self):
        res = self.client.post(self.login_url, {'username': 'loginuser', 'password': 'testpass456'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_login_wrong_password(self):
        res = self.client.post(self.login_url, {'username': 'loginuser', 'password': 'wrongpass'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        res = self.client.post(self.login_url, {'username': 'ghost', 'password': 'pass'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenVerificationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.verify_url = reverse('verify-token')
        self.user = CentralUser.objects.create_user(
            username='verifyuser',
            name='Verify User',
            roll_number='23CS003',
            hostel_number='H5',
            password='verifypass789',
        )
        login_res = self.client.post(reverse('login'), {'username': 'verifyuser', 'password': 'verifypass789'}, format='json')
        self.access_token = login_res.data['access']

    def test_verify_valid_token(self):
        res = self.client.post(self.verify_url, {'token': self.access_token}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['valid'])
        self.assertEqual(res.data['user']['roll_number'], '23CS003')

    def test_verify_invalid_token(self):
        res = self.client.post(self.verify_url, {'token': 'this.is.not.valid'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(res.data['valid'])

    def test_verify_missing_token(self):
        res = self.client.post(self.verify_url, {}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_me_endpoint_requires_auth(self):
        res = self.client.get(reverse('me'))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_endpoint_with_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        res = self.client.get(reverse('me'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], 'verifyuser')
