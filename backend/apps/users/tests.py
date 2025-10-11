from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from .models import User

class UserRegistrationTests(TestCase):
    def setUp(self):
        self.valid_payload = {
            'email': 'test@example.com',
            'password': 'testpassword'
        }
        self.invalid_payload = {
            'email': 'invalidemail',
            'password': 'short'
        }

    def test_valid_user_registration(self):
        response = self.client.post(reverse('user-register'), self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')

    def test_invalid_user_registration(self):
        response = self.client.post(reverse('user-register'), self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_username_creation_from_email(self):
        response = self.client.post(reverse('user-register'), self.valid_payload, format='json')
        user = User.objects.get()
        self.assertEqual(user.username, 'test')  # Assuming username is derived from email before '@'

    def test_unique_key_generation(self):
        response = self.client.post(reverse('user-register'), self.valid_payload, format='json')
        user = User.objects.get()
        self.assertEqual(len(user.unique_key), 8)  # Check if unique key is 8 characters long
        self.assertTrue(user.unique_key.isalnum())  # Check if unique key is alphanumeric

    # Additional tests can be added here for other functionalities related to user management.