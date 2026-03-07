"""Tests for admin programs API (majors, programs, etc.)."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from programs.models import Major

User = get_user_model()


def _create_admin():
    return User.objects.create_superuser(
        username="admin@ex.com", email="admin@ex.com", password="admin123"
    )


class AdminMajorAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = _create_admin()
        self.url = "/api/v1/programs/admin/majors/"

    def test_list_majors_admin(self):
        Major.objects.create(code="M2CS", name="Master CS")
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("majors", resp.json())
        self.assertEqual(len(resp.json()["majors"]), 1)
        self.assertEqual(resp.json()["majors"][0]["code"], "M2CS")

    def test_create_major_admin(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(
            self.url,
            {"code": "M2DS", "name": "Master Data Science"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data["code"], "M2DS")
        self.assertEqual(data["name"], "Master Data Science")
        self.assertTrue(Major.objects.filter(code="M2DS").exists())
