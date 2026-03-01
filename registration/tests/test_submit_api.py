from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Person
from registration.enums import RegistrationStatus, RegistrationStep
from registration.models import RegistrationSession

User = get_user_model()


def _create_user_with_person(email, full_name="Test"):
    user = User.objects.create_user(username=email, email=email, password="testpass123")
    person = Person.objects.create(full_name=full_name, email=email, user=user)
    return user, person


class RegistrationSubmitAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/registration/submit/"

    def test_post_unauthenticated_returns_403(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertIn(response.status_code, (401, 403))

    def test_post_with_no_session_returns_404(self):
        user, person = _create_user_with_person("test@example.com")
        self.client.force_authenticate(user=user)
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 404)

    def test_post_when_not_at_submit_step_returns_400(self):
        user, person = _create_user_with_person("test2@example.com")
        RegistrationSession.objects.create(
            person=person,
            current_step=RegistrationStep.Q1_MASTER_STATUS.value,
            status=RegistrationStatus.PENDING.value,
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("submit", response.json()["detail"].lower())

    def test_post_when_already_submitted_returns_400(self):
        user, person = _create_user_with_person("test3@example.com")
        RegistrationSession.objects.create(
            person=person,
            current_step=RegistrationStep.SUBMIT.value,
            status=RegistrationStatus.SUBMITTED.value,
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_post_when_at_submit_step_succeeds(self):
        user, person = _create_user_with_person("test4@example.com")
        session = RegistrationSession.objects.create(
            person=person,
            current_step=RegistrationStep.SUBMIT.value,
            status=RegistrationStatus.PENDING.value,
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], RegistrationStatus.SUBMITTED.value)
        self.assertIn("submitted", data["message"].lower())
        session.refresh_from_db()
        self.assertEqual(session.status, RegistrationStatus.SUBMITTED.value)
