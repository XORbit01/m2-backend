from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Person

User = get_user_model()


def _create_user_with_person(email, password="testpass123"):
    user = User.objects.create_user(username=email, email=email, password=password)
    person = Person.objects.create(full_name="Test", email=email, user=user)
    return user, person


class LoginAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/auth/login/"

    def test_login_invalid_credentials_returns_401(self):
        response = self.client.post(
            self.url,
            {"email": "bad@example.com", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_login_success_returns_registration_status_and_tokens(self):
        user, person = _create_user_with_person("test@example.com")
        response = self.client.post(
            self.url,
            {"email": "test@example.com", "password": "testpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["person_id"], person.id)
        self.assertFalse(data["registration_complete"])
        self.assertEqual(data["current_step"], "Q1_MASTER_STATUS")
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)


class MeAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/auth/me/"

    def test_me_unauthenticated_returns_403(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, (401, 403))

    def test_me_authenticated_returns_user_and_registration_status(self):
        user, person = _create_user_with_person("me@example.com")
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], "me@example.com")
        self.assertEqual(data["person_id"], person.id)
        self.assertFalse(data["registration_complete"])
