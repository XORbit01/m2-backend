"""Tests for admin create teacher API."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from profiles.models import TeacherProfile

User = get_user_model()


class CreateTeacherAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/auth/admin/teachers/"
        self.admin = User.objects.create_superuser(
            username="admin@example.com",
            email="admin@example.com",
            password="adminpass123",
        )

    def test_post_unauthenticated_returns_403(self):
        response = self.client.post(
            self.url,
            {
                "email": "teacher@example.com",
                "password": "teachpass123",
                "full_name": "Dr. Smith",
                "title": "Professor",
                "department": "CS",
                "is_supervisor": True,
            },
            format="json",
        )
        self.assertIn(response.status_code, (401, 403))

    def test_post_as_admin_creates_teacher(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            self.url,
            {
                "email": "teacher@example.com",
                "password": "teachpass123",
                "full_name": "Dr. Smith",
                "title": "Professor",
                "department": "CS",
                "is_supervisor": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["email"], "teacher@example.com")
        self.assertEqual(data["full_name"], "Dr. Smith")
        self.assertTrue(data["is_supervisor"])
        self.assertTrue(
            TeacherProfile.objects.filter(
                person__email="teacher@example.com"
            ).exists()
        )
