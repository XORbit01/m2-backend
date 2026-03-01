from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Person
from registration.enums import BaseRole, RegistrationStep
from registration.models import RegistrationSession

User = get_user_model()


def _create_user_with_person(email, full_name="Test"):
    user = User.objects.create_user(username=email, email=email, password="testpass123")
    person = Person.objects.create(full_name=full_name, email=email, user=user)
    return user, person


class RegistrationAnswerAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/registration/answer/"

    def test_post_unauthenticated_returns_403(self):
        response = self.client.post(self.url, {"finished_master": False}, format="json")
        self.assertIn(response.status_code, (401, 403))

    def test_post_q1_student_path_advances_to_collect_student_data(self):
        user, person = _create_user_with_person("test@example.com")
        self.client.force_authenticate(user=user)
        response = self.client.post(
            self.url,
            {"finished_master": False},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["current_step"], RegistrationStep.COLLECT_STUDENT_DATA.value)
        self.assertEqual(data["base_role"], BaseRole.STUDENT.value)

    def test_post_q1_alumni_path_advances_to_collect_alumni_data(self):
        user, person = _create_user_with_person("test2@example.com")
        self.client.force_authenticate(user=user)
        response = self.client.post(
            self.url,
            {"finished_master": True},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["current_step"], RegistrationStep.COLLECT_ALUMNI_DATA.value)
        self.assertEqual(data["base_role"], BaseRole.ALUMNI.value)

    def test_post_when_already_submitted_returns_400(self):
        user, person = _create_user_with_person("test3@example.com")
        RegistrationSession.objects.create(
            person=person,
            status="SUBMITTED",
            current_step=RegistrationStep.SUBMIT.value,
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(
            self.url,
            {"finished_master": False},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("submitted", response.json()["detail"].lower())

    def test_post_with_invalid_transition_returns_400(self):
        user, person = _create_user_with_person("test4@example.com")
        RegistrationSession.objects.create(
            person=person,
            current_step=RegistrationStep.Q1_MASTER_STATUS.value,
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 400)
