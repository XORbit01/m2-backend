from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Person

User = get_user_model()


def _create_admin(email="admin@example.com", password="adminpass123"):
    return User.objects.create_superuser(
        username=email, email=email, password=password
    )


class CreateUserAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/auth/admin/users/"

    def test_create_user_unauthenticated_returns_403(self):
        response = self.client.post(
            self.url,
            {
                "email": "new@example.com",
                "password": "TempPass123",
                "full_name": "New User",
            },
            format="json",
        )
        self.assertIn(response.status_code, (401, 403))

    def test_create_user_non_admin_returns_403(self):
        user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="pass123",
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(
            self.url,
            {
                "email": "new@example.com",
                "password": "TempPass123",
                "full_name": "New User",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_create_user_admin_succeeds(self):
        admin = _create_admin()
        self.client.force_authenticate(user=admin)
        response = self.client.post(
            self.url,
            {
                "email": "student@example.com",
                "password": "TempPass123",
                "full_name": "John Doe",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["email"], "student@example.com")
        self.assertEqual(data["full_name"], "John Doe")
        self.assertIn("user_id", data)
        self.assertIn("person_id", data)
        user = User.objects.get(email="student@example.com")
        person = Person.objects.get(email="student@example.com")
        self.assertEqual(person.user, user)
        self.assertTrue(user.check_password("TempPass123"))

    def test_create_user_duplicate_email_returns_400(self):
        admin = _create_admin()
        Person.objects.create(full_name="Existing", email="dup@example.com")
        self.client.force_authenticate(user=admin)
        response = self.client.post(
            self.url,
            {
                "email": "dup@example.com",
                "password": "TempPass123",
                "full_name": "Duplicate",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
