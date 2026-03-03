"""Tests for profile settings API."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from core.models import Person

User = get_user_model()


def _create_user_with_person(email, full_name="Test User", password="testpass123"):
    user = User.objects.create_user(username=email, email=email, password=password)
    person = Person.objects.create(full_name=full_name, email=email, user=user)
    return user, person


class ProfileSettingsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/auth/profile/"
        self.user, self.person = _create_user_with_person(
            "me@example.com", "Initial Name"
        )

    def test_get_unauthenticated_returns_403(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, (401, 403))

    def test_get_profile_returns_basic_info(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["first_name"], "Initial")
        self.assertEqual(data["last_name"], "Name")
        self.assertEqual(data["email"], "me@example.com")
        self.assertIsNone(data["avatar_url"])

    def test_update_full_name_and_avatar(self):
        self.client.force_authenticate(user=self.user)
        # Fake small image file (content type not enforced server-side)
        avatar_file = SimpleUploadedFile(
            "avatar.png", b"fake-image-content", content_type="image/png"
        )
        response = self.client.put(
            self.url,
            {"first_name": "Updated", "last_name": "Name", "avatar": avatar_file},
            format="multipart",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["first_name"], "Updated")
        self.assertEqual(data["last_name"], "Name")
        self.person.refresh_from_db()
        self.assertEqual(self.person.full_name, "Updated Name")
        self.assertIsNotNone(self.person.avatar)

