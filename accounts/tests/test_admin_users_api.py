"""Tests for admin user list, retrieve, update, delete API."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Person

User = get_user_model()


def _create_admin(email="admin@example.com", password="adminpass123"):
    return User.objects.create_superuser(
        username=email, email=email, password=password
    )


class AdminUserListAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/auth/admin/users/"

    def test_list_unauthenticated_returns_403(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, (401, 403))

    def test_list_admin_succeeds(self):
        admin = _create_admin()
        user = User.objects.create_user(
            username="u@ex.com", email="u@ex.com", password="pass"
        )
        Person.objects.create(full_name="User", email="u@ex.com", user=user)
        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("users", data)
        self.assertGreaterEqual(len(data["users"]), 2)  # admin + user


class AdminUserDetailAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = _create_admin()
        self.user = User.objects.create_user(
            username="target@ex.com", email="target@ex.com", password="pass"
        )
        self.person = Person.objects.create(
            full_name="Target", email="target@ex.com", user=self.user
        )

    def test_retrieve_admin_succeeds(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            f"/api/v1/auth/admin/users/{self.user.id}/"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user_id"], self.user.id)
        self.assertEqual(data["email"], "target@ex.com")
        self.assertEqual(data["full_name"], "Target")
        self.assertIn("roles", data)

    def test_update_admin_succeeds(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(
            f"/api/v1/auth/admin/users/{self.user.id}/",
            {"full_name": "Updated Name", "email": "updated@ex.com"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["full_name"], "Updated Name")
        self.assertEqual(data["email"], "updated@ex.com")
        self.user.refresh_from_db()
        self.person.refresh_from_db()
        self.assertEqual(self.user.email, "updated@ex.com")
        self.assertEqual(self.person.full_name, "Updated Name")

    def test_delete_admin_succeeds(self):
        self.client.force_authenticate(user=self.admin)
        uid = self.user.id
        response = self.client.delete(
            f"/api/v1/auth/admin/users/{uid}/"
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(User.objects.filter(id=uid).exists())
        self.assertFalse(Person.objects.filter(id=self.person.id).exists())
