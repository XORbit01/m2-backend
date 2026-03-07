"""Tests for public guest registration API."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Person
from profiles.models import GuestProfile

User = get_user_model()


class GuestRegisterAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/auth/register/guest/"

    def test_register_guest_succeeds_unauthenticated(self):
        response = self.client.post(
            self.url,
            {
                "email": "guest@example.com",
                "password": "GuestPass123",
                "full_name": "Guest User",
                "note": "Optional note",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["email"], "guest@example.com")
        self.assertEqual(data["full_name"], "Guest User")
        self.assertIn("user_id", data)
        self.assertIn("person_id", data)
        user = User.objects.get(email="guest@example.com")
        person = Person.objects.get(email="guest@example.com")
        self.assertEqual(person.user, user)
        self.assertTrue(user.check_password("GuestPass123"))
        guest = GuestProfile.objects.get(person=person)
        self.assertEqual(guest.note, "Optional note")

    def test_register_guest_without_note(self):
        response = self.client.post(
            self.url,
            {
                "email": "guest2@example.com",
                "password": "GuestPass123",
                "full_name": "Another Guest",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        person = Person.objects.get(email="guest2@example.com")
        guest = GuestProfile.objects.get(person=person)
        self.assertEqual(guest.note, "")

    def test_register_guest_duplicate_email_returns_400(self):
        User.objects.create_user(
            username="existing@example.com",
            email="existing@example.com",
            password="existingpass",
        )
        response = self.client.post(
            self.url,
            {
                "email": "existing@example.com",
                "password": "GuestPass123",
                "full_name": "Guest",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())
