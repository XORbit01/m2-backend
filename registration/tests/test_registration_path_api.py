"""
Integration test: full registration flow via API endpoints only.
Runs the chosen path (student, no internship, not working) by calling
GET state, POST answer, POST submit in sequence.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Person
from programs.models import Major
from registration.enums import BaseRole, RegistrationStep
from registration.models import RegistrationSession

User = get_user_model()


def _create_user_with_person(email, full_name="Test", password="testpass123"):
    user = User.objects.create_user(username=email, email=email, password=password)
    person = Person.objects.create(full_name=full_name, email=email, user=user)
    return user, person


class RegistrationPathAPITestCase(TestCase):
    """
    Test path: student, no internship, not working.
    Endpoints: GET state -> POST answer (Q1) -> POST answer (student_data) ->
               POST answer (has_internship false) -> POST answer (is_working false) -> POST submit.
    """

    def setUp(self):
        self.client = APIClient()
        self.major = Major.objects.create(code="M2CS", name="Master CS")
        self.user, self.person = _create_user_with_person("path@example.com")
        self.client.force_authenticate(user=self.user)

    def test_full_student_path_minimal_via_api(self):
        state_url = "/api/v1/registration/state/"
        answer_url = "/api/v1/registration/answer/"
        submit_url = "/api/v1/registration/submit/"

        # 1) GET state -> Q1_MASTER_STATUS
        r = self.client.get(state_url)
        self.assertEqual(r.status_code, 200, r.json())
        data = r.json()
        self.assertEqual(data["current_step"], RegistrationStep.Q1_MASTER_STATUS.value)
        self.assertEqual(data["question"]["question_key"], "finished_master")

        # 2) POST answer Q1: student path
        r = self.client.post(answer_url, {"finished_master": False}, format="json")
        self.assertEqual(r.status_code, 200, r.json())
        data = r.json()
        self.assertEqual(data["current_step"], RegistrationStep.COLLECT_STUDENT_DATA.value)
        self.assertEqual(data["base_role"], BaseRole.STUDENT.value)

        # 3) POST answer: student_data
        r = self.client.post(
            answer_url,
            {
                "student_data": {
                    "major_id": self.major.id,
                    "student_number": "M2-2024-001",
                    "cohort_year": "2024",
                }
            },
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.json())
        data = r.json()
        self.assertEqual(data["current_step"], RegistrationStep.Q2_INTERNSHIP.value)

        # 4) POST answer: no internship
        r = self.client.post(answer_url, {"has_internship": False}, format="json")
        self.assertEqual(r.status_code, 200, r.json())
        data = r.json()
        self.assertEqual(data["current_step"], RegistrationStep.Q4_WORK.value)

        # 5) POST answer: not working
        r = self.client.post(answer_url, {"is_working": False}, format="json")
        self.assertEqual(r.status_code, 200, r.json())
        data = r.json()
        self.assertEqual(data["current_step"], RegistrationStep.SUBMIT.value)
        self.assertEqual(data["question"]["question_type"], "submit")

        # 6) POST submit
        r = self.client.post(submit_url, {}, format="json")
        self.assertEqual(r.status_code, 200, r.json())
        data = r.json()
        self.assertEqual(data["status"], "SUBMITTED")

        session = RegistrationSession.objects.get(person=self.person)
        self.assertEqual(session.status, "SUBMITTED")
        self.assertEqual(session.current_step, RegistrationStep.SUBMIT.value)
        self.assertIn("student", session.payload)
        self.assertEqual(session.payload["student"]["major_id"], self.major.id)
