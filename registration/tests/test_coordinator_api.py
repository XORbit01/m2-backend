"""
Tests for major coordinator verification API: list pending, accept, reject.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.enums import ExperienceType, InstitutionType
from core.models import Person
from experience.models import Experience
from institutions.models import Institution
from profiles.models import AlumniProfile, StudentProfile
from programs.models import Major, MajorCoordinator
from registration.enums import BaseRole, RegistrationStatus, RegistrationStep
from registration.models import RegistrationSession

User = get_user_model()


def _create_user_with_person(email, full_name="Test", password="testpass123"):
    user = User.objects.create_user(username=email, email=email, password=password)
    person = Person.objects.create(full_name=full_name, email=email, user=user)
    return user, person


class CoordinatorPendingListAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/registration/coordinator/pending/"
        self.major = Major.objects.create(code="M2CS", name="Master CS")

    def test_get_unauthenticated_returns_403(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, (401, 403))

    def test_get_with_no_person_returns_403(self):
        user = User.objects.create_user(
            username="noperson@example.com",
            email="noperson@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertIn("person", response.json()["detail"].lower())

    def test_get_when_not_coordinator_returns_empty_list(self):
        user, person = _create_user_with_person("notcoord@example.com")
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sessions"], [])

    def test_get_when_coordinator_returns_submitted_sessions_for_that_major(self):
        coord_user, coord_person = _create_user_with_person("coord@example.com")
        MajorCoordinator.objects.create(
            major=self.major, coordinator=coord_person, is_primary=True
        )
        applicant_user, applicant_person = _create_user_with_person("applicant@example.com")
        RegistrationSession.objects.create(
            person=applicant_person,
            current_step=RegistrationStep.SUBMIT.value,
            status=RegistrationStatus.SUBMITTED.value,
            base_role=BaseRole.STUDENT.value,
            payload={"student": {"major_id": self.major.id}},
        )
        self.client.force_authenticate(user=coord_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        sessions = response.json()["sessions"]
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]["person_id"], applicant_person.id)
        self.assertEqual(sessions[0]["payload"]["student"]["major_id"], self.major.id)


class CoordinatorAcceptAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.major = Major.objects.create(code="M2CS", name="Master CS")

    def _accept_url(self, session_id):
        return f"/api/v1/registration/coordinator/{session_id}/accept/"

    def test_post_unauthenticated_returns_403(self):
        response = self.client.post(self._accept_url(1), {}, format="json")
        self.assertIn(response.status_code, (401, 403))

    def test_post_unknown_session_returns_404(self):
        user, person = _create_user_with_person("u@example.com")
        self.client.force_authenticate(user=user)
        response = self.client.post(self._accept_url(99999), {}, format="json")
        self.assertEqual(response.status_code, 404)

    def test_post_when_not_coordinator_for_major_returns_403(self):
        user, person = _create_user_with_person("other@example.com")
        applicant_user, applicant_person = _create_user_with_person("applicant@example.com")
        session = RegistrationSession.objects.create(
            person=applicant_person,
            current_step=RegistrationStep.SUBMIT.value,
            status=RegistrationStatus.SUBMITTED.value,
            base_role=BaseRole.STUDENT.value,
            payload={"student": {"major_id": self.major.id}},
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(self._accept_url(session.id), {}, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertIn("Not allowed", response.json()["detail"])

    def test_post_when_coordinator_accepts_sets_status_accepted(self):
        coord_user, coord_person = _create_user_with_person("coord@example.com")
        MajorCoordinator.objects.create(
            major=self.major, coordinator=coord_person, is_primary=True
        )
        applicant_user, applicant_person = _create_user_with_person("applicant@example.com")
        session = RegistrationSession.objects.create(
            person=applicant_person,
            current_step=RegistrationStep.SUBMIT.value,
            status=RegistrationStatus.SUBMITTED.value,
            base_role=BaseRole.STUDENT.value,
            payload={"student": {"major_id": self.major.id}},
        )
        self.client.force_authenticate(user=coord_user)
        response = self.client.post(self._accept_url(session.id), {}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], RegistrationStatus.ACCEPTED.value)
        session.refresh_from_db()
        self.assertEqual(session.status, RegistrationStatus.ACCEPTED.value)

    def test_post_accept_creates_student_profile_from_payload(self):
        coord_user, coord_person = _create_user_with_person("coord@example.com")
        MajorCoordinator.objects.create(
            major=self.major, coordinator=coord_person, is_primary=True
        )
        applicant_user, applicant_person = _create_user_with_person("applicant@example.com")
        session = RegistrationSession.objects.create(
            person=applicant_person,
            current_step=RegistrationStep.SUBMIT.value,
            status=RegistrationStatus.SUBMITTED.value,
            base_role=BaseRole.STUDENT.value,
            payload={
                "student": {
                    "major_id": self.major.id,
                    "student_number": "M2-2024-001",
                    "cohort_year": "2024",
                }
            },
        )
        self.assertFalse(StudentProfile.objects.filter(person=applicant_person).exists())
        self.client.force_authenticate(user=coord_user)
        response = self.client.post(self._accept_url(session.id), {}, format="json")
        self.assertEqual(response.status_code, 200)
        profile = StudentProfile.objects.get(person=applicant_person)
        self.assertEqual(profile.student_number, "M2-2024-001")
        self.assertEqual(profile.current_status, "ACTIVE")

    def test_post_accept_creates_alumni_profile_from_payload(self):
        coord_user, coord_person = _create_user_with_person("coord@example.com")
        MajorCoordinator.objects.create(
            major=self.major, coordinator=coord_person, is_primary=True
        )
        applicant_user, applicant_person = _create_user_with_person("alumni@example.com")
        session = RegistrationSession.objects.create(
            person=applicant_person,
            current_step=RegistrationStep.SUBMIT.value,
            status=RegistrationStatus.SUBMITTED.value,
            base_role=BaseRole.ALUMNI.value,
            payload={
                "alumni": {"major_id": self.major.id, "graduation_year": "2023"}
            },
        )
        self.assertFalse(AlumniProfile.objects.filter(person=applicant_person).exists())
        self.client.force_authenticate(user=coord_user)
        response = self.client.post(self._accept_url(session.id), {}, format="json")
        self.assertEqual(response.status_code, 200)
        profile = AlumniProfile.objects.get(person=applicant_person)
        self.assertEqual(profile.graduation_year, 2023)

    def test_post_accept_creates_experiences_from_internship_phd_work_payload(self):
        inst = Institution.objects.create(
            name="Sorbonne University",
            country="France",
            type=InstitutionType.UNIVERSITY.value,
        )
        coord_user, coord_person = _create_user_with_person("coord@example.com")
        MajorCoordinator.objects.create(
            major=self.major, coordinator=coord_person, is_primary=True
        )
        applicant_user, applicant_person = _create_user_with_person("applicant@example.com")
        session = RegistrationSession.objects.create(
            person=applicant_person,
            current_step=RegistrationStep.SUBMIT.value,
            status=RegistrationStatus.SUBMITTED.value,
            base_role=BaseRole.STUDENT.value,
            payload={
                "student": {
                    "major_id": self.major.id,
                    "student_number": "M2-2024-002",
                    "cohort_year": "2024",
                },
                "internships": [
                    {
                        "institution_name": inst.name,
                        "department": "Research Lab",
                        "country": "France",
                        "start_date": "2024-01-01",
                        "end_date": "2024-06-30",
                    }
                ],
                "phd": [
                    {
                        "institution_name": inst.name,
                        "field": "ML",
                        "lab_name": "AI Lab",
                        "start_date": "2024-09-01",
                        "end_date": None,
                    }
                ],
                "work": [
                    {
                        "institution_name": inst.name,
                        "title": "Data Scientist",
                        "country": "France",
                        "start_date": "2024-01-01",
                        "end_date": None,
                    }
                ],
            },
        )
        self.assertEqual(Experience.objects.filter(person=applicant_person).count(), 0)
        self.client.force_authenticate(user=coord_user)
        response = self.client.post(self._accept_url(session.id), {}, format="json")
        self.assertEqual(response.status_code, 200)
        experiences = list(Experience.objects.filter(person=applicant_person).order_by("type"))
        self.assertEqual(len(experiences), 3)
        by_type = {e.type: e for e in experiences}
        self.assertIn(ExperienceType.STAGE.value, by_type)
        self.assertEqual(by_type[ExperienceType.STAGE.value].title, "Research Lab")
        self.assertIn(ExperienceType.DOCTORATE.value, by_type)
        self.assertEqual(by_type[ExperienceType.DOCTORATE.value].title, "ML")
        self.assertEqual(by_type[ExperienceType.DOCTORATE.value].lab_name, "AI Lab")
        self.assertIn(ExperienceType.JOB.value, by_type)
        self.assertEqual(by_type[ExperienceType.JOB.value].title, "Data Scientist")


class CoordinatorRejectAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.major = Major.objects.create(code="M2CS", name="Master CS")

    def _reject_url(self, session_id):
        return f"/api/v1/registration/coordinator/{session_id}/reject/"

    def test_post_unauthenticated_returns_403(self):
        response = self.client.post(self._reject_url(1), {}, format="json")
        self.assertIn(response.status_code, (401, 403))

    def test_post_unknown_session_returns_404(self):
        user, person = _create_user_with_person("u@example.com")
        self.client.force_authenticate(user=user)
        response = self.client.post(self._reject_url(99999), {}, format="json")
        self.assertEqual(response.status_code, 404)

    def test_post_when_not_coordinator_returns_403(self):
        user, person = _create_user_with_person("other@example.com")
        applicant_user, applicant_person = _create_user_with_person("applicant@example.com")
        session = RegistrationSession.objects.create(
            person=applicant_person,
            current_step=RegistrationStep.SUBMIT.value,
            status=RegistrationStatus.SUBMITTED.value,
            base_role=BaseRole.STUDENT.value,
            payload={"student": {"major_id": self.major.id}},
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(self._reject_url(session.id), {}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_post_when_coordinator_rejects_deletes_session(self):
        coord_user, coord_person = _create_user_with_person("coord@example.com")
        MajorCoordinator.objects.create(
            major=self.major, coordinator=coord_person, is_primary=True
        )
        applicant_user, applicant_person = _create_user_with_person("applicant@example.com")
        session = RegistrationSession.objects.create(
            person=applicant_person,
            current_step=RegistrationStep.SUBMIT.value,
            status=RegistrationStatus.SUBMITTED.value,
            base_role=BaseRole.STUDENT.value,
            payload={"student": {"major_id": self.major.id}},
        )
        session_id = session.id
        self.client.force_authenticate(user=coord_user)
        response = self.client.post(self._reject_url(session_id), {}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("rejected", response.json()["message"].lower())
        self.assertFalse(RegistrationSession.objects.filter(pk=session_id).exists())
