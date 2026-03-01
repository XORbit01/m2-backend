from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Person
from programs.models import Major
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
        self.assertIn("question", data)
        self.assertIsNotNone(data["question"])
        self.assertEqual(data["question"]["question_type"], "object")
        self.assertEqual(data["question"]["question_key"], "student_data")
        self.assertIn("fields", data["question"])
        self.assertGreater(len(data["question"]["fields"]), 0)

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
        self.assertIn("question", data)
        self.assertEqual(data["question"]["question_key"], "alumni_data")
        self.assertEqual(data["question"]["question_type"], "object")

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

    def test_post_student_data_with_invalid_major_returns_400(self):
        user, person = _create_user_with_person("student_invalid@example.com")
        RegistrationSession.objects.create(
            person=person,
            current_step=RegistrationStep.COLLECT_STUDENT_DATA.value,
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(
            self.url,
            {
                "student_data": {
                    "major_id": 99999,
                    "student_number": "M2-2024-001",
                    "cohort_year": "2024",
                }
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("errors", data)
        self.assertIn("student_data.major_id", data["errors"])

    def test_post_student_data_with_valid_major_advances(self):
        major = Major.objects.create(code="M2CS", name="Master CS")
        user, person = _create_user_with_person("student_valid@example.com")
        RegistrationSession.objects.create(
            person=person,
            current_step=RegistrationStep.COLLECT_STUDENT_DATA.value,
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(
            self.url,
            {
                "student_data": {
                    "major_id": major.id,
                    "student_number": "M2-2024-001",
                    "cohort_year": "2024",
                }
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["current_step"], RegistrationStep.Q2_INTERNSHIP.value)
