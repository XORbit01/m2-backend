from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Person
from registration.enums import RegistrationStep

User = get_user_model()


def _create_user_with_person(email, full_name="Test User"):
    user = User.objects.create_user(username=email, email=email, password="testpass123")
    person = Person.objects.create(full_name=full_name, email=email, user=user)
    return user, person


class RegistrationStateAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/registration/state/"

    def test_get_state_unauthenticated_returns_403(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, (401, 403))

    def test_get_state_with_valid_user_creates_session_and_returns_state(self):
        user, person = _create_user_with_person("test@example.com")
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["current_step"], RegistrationStep.Q1_MASTER_STATUS.value)
        self.assertEqual(data["payload"], {})
        self.assertIsNone(data["base_role"])
        self.assertEqual(data["status"], "PENDING")
        self.assertEqual(data["next_question_key"], "finished_master")

    def test_get_state_with_existing_session_returns_same_session(self):
        user, person = _create_user_with_person("test2@example.com")
        from registration.models import RegistrationSession

        session, _ = RegistrationSession.objects.get_or_create(
            person=person,
            defaults={
                "current_step": RegistrationStep.Q2_INTERNSHIP.value,
                "payload": {"student": {"major_id": 1}},
            },
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["current_step"], RegistrationStep.Q2_INTERNSHIP.value)
        self.assertEqual(data["payload"]["student"]["major_id"], 1)

    def test_get_state_user_without_person_returns_403(self):
        user = User.objects.create_user(
            username="noperson@example.com",
            email="noperson@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
