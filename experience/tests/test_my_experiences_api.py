"""Tests for my experiences API."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.enums import ExperienceStatus, ExperienceType
from core.models import Person
from experience.models import Experience
from institutions.models import Institution

User = get_user_model()


def _create_user_with_person(email, full_name="Test", password="testpass123"):
    user = User.objects.create_user(username=email, email=email, password=password)
    person = Person.objects.create(full_name=full_name, email=email, user=user)
    return user, person


class MyExperiencesAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/experience/me/"
        self.user, self.person = _create_user_with_person("me@example.com", "Student")
        self.institution = Institution.objects.create(
            name="Test University",
            type="UNIVERSITY",
            country="FR",
        )
        self.experience = Experience.objects.create(
            person=self.person,
            type=ExperienceType.STAGE.value,
            status=ExperienceStatus.ONGOING.value,
            institution=self.institution,
            title="Internship",
            idea="Research on AI",
        )

    def test_get_unauthenticated_returns_403(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, (401, 403))

    def test_get_returns_experiences_for_person(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("experiences", data)
        self.assertEqual(len(data["experiences"]), 1)
        exp = data["experiences"][0]
        self.assertEqual(exp["title"], "Internship")
        self.assertEqual(exp["institution_name"], "Test University")

    def test_post_creates_experience_for_person(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url,
            {
                "type": ExperienceType.STAGE.value,
                "status": ExperienceStatus.PLANNED.value,
                "institution_id": self.institution.id,
                "title": "New Internship",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["title"], "New Internship")
        self.assertEqual(data["institution_id"], self.institution.id)

    def test_put_updates_own_experience(self):
        self.client.force_authenticate(user=self.user)
        detail_url = f"/api/v1/experience/me/{self.experience.id}/"
        response = self.client.put(
            detail_url,
            {
                "status": ExperienceStatus.COMPLETED.value,
                "idea": "Updated idea",
                "keywords": "updated",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], ExperienceStatus.COMPLETED.value)
        self.assertEqual(data["idea"], "Updated idea")

    def test_delete_own_experience(self):
        self.client.force_authenticate(user=self.user)
        detail_url = f"/api/v1/experience/me/{self.experience.id}/"
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Experience.objects.filter(id=self.experience.id).exists()
        )

