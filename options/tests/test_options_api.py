"""Tests for public and admin options API."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from programs.models import Major

User = get_user_model()


def _create_admin():
    return User.objects.create_superuser(
        username="admin@ex.com", email="admin@ex.com", password="admin123"
    )


class OptionsMajorsPublicTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/options/majors/"

    def test_get_majors_public_no_auth(self):
        Major.objects.create(code="M2CS", name="Master CS")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("majors", data)
        self.assertEqual(len(data["majors"]), 1)
        self.assertEqual(data["majors"][0]["code"], "M2CS")
        self.assertEqual(data["majors"][0]["name"], "Master CS")


class AdminOptionsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = _create_admin()
        self.url = "/api/v1/options/admin/"

    def test_get_admin_options_requires_auth(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 401)

    def test_get_admin_options_as_admin(self):
        Major.objects.create(code="M2CS", name="Master CS")
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("majors", data)
        self.assertIn("programs", data)
        self.assertIn("cohorts", data)
        self.assertIn("courses", data)
        self.assertIn("semesters", data)
        self.assertIn("institutions", data)
        self.assertIn("institution_types", data)
        self.assertIn("teachers", data)
        self.assertEqual(len(data["majors"]), 1)
        self.assertEqual(data["majors"][0]["code"], "M2CS")
