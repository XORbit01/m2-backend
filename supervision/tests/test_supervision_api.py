"""Tests for student and teacher supervision APIs."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Person
from profiles.models import StudentProfile, TeacherProfile
from supervision.models import Supervision

User = get_user_model()


def _create_user_with_person(email, full_name="Test", password="testpass123"):
    user = User.objects.create_user(username=email, email=email, password=password)
    person = Person.objects.create(full_name=full_name, email=email, user=user)
    return user, person


class StudentSupervisionAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/supervision/student/requests/"

        # Create teacher available as supervisor
        self.teacher_user, self.teacher_person = _create_user_with_person(
            "teacher@example.com", "Dr. Smith"
        )
        TeacherProfile.objects.create(
            person=self.teacher_person,
            title="Professor",
            department="CS",
            is_supervisor=True,
        )

        # Create student
        self.student_user, self.student_person = _create_user_with_person(
            "student@example.com", "Alice"
        )
        StudentProfile.objects.create(
            person=self.student_person,
            student_number="M2-001",
            current_status="ACTIVE",
        )

    def _cancel_url(self, supervision_id):
        return f"/api/v1/supervision/student/requests/{supervision_id}/cancel/"

    def test_get_unauthenticated_returns_403(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, (401, 403))

    def test_post_unauthenticated_returns_403(self):
        response = self.client.post(
            self.url,
            {"teacher_id": self.teacher_person.id},
            format="json",
        )
        self.assertIn(response.status_code, (401, 403))

    def test_student_can_create_supervision_request(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(
            self.url,
            {"teacher_id": self.teacher_person.id},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["teacher_id"], self.teacher_person.id)
        self.assertEqual(data["status"], "PENDING")
        self.assertTrue(
            Supervision.objects.filter(
                student=self.student_person,
                teacher=self.teacher_person,
                status="PENDING",
            ).exists()
        )

    def test_student_list_returns_created_supervisions(self):
        Supervision.objects.create(
            student=self.student_person,
            teacher=self.teacher_person,
            status="PENDING",
        )
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["supervisions"]), 1)
        item = data["supervisions"][0]
        self.assertEqual(item["teacher_id"], self.teacher_person.id)
        self.assertEqual(item["teacher_name"], "Dr. Smith")
        self.assertEqual(item["status"], "PENDING")

    def test_student_cannot_request_same_supervision_twice_while_pending(self):
        Supervision.objects.create(
            student=self.student_person,
            teacher=self.teacher_person,
            status="PENDING",
        )
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(
            self.url,
            {"teacher_id": self.teacher_person.id},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_student_can_cancel_pending_request(self):
        supervision = Supervision.objects.create(
            student=self.student_person,
            teacher=self.teacher_person,
            status="PENDING",
        )
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self._cancel_url(supervision.id), {}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Supervision.objects.filter(
                id=supervision.id,
            ).exists()
        )

    def test_student_cannot_cancel_non_pending_request(self):
        supervision = Supervision.objects.create(
            student=self.student_person,
            teacher=self.teacher_person,
            status="APPROVED",
        )
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self._cancel_url(supervision.id), {}, format="json")
        self.assertEqual(response.status_code, 400)


class TeacherSupervisionAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_url = "/api/v1/supervision/teacher/requests/"

        # Create teacher
        self.teacher_user, self.teacher_person = _create_user_with_person(
            "teacher@example.com", "Dr. Smith"
        )
        TeacherProfile.objects.create(
            person=self.teacher_person,
            title="Professor",
            department="CS",
            is_supervisor=True,
        )

        # Create student and supervision
        self.student_user, self.student_person = _create_user_with_person(
            "student@example.com", "Alice"
        )
        StudentProfile.objects.create(
            person=self.student_person,
            student_number="M2-001",
            current_status="ACTIVE",
        )
        self.supervision = Supervision.objects.create(
            student=self.student_person,
            teacher=self.teacher_person,
            status="PENDING",
        )

    def _approve_url(self, supervision_id):
        return f"/api/v1/supervision/teacher/requests/{supervision_id}/approve/"

    def _reject_url(self, supervision_id):
        return f"/api/v1/supervision/teacher/requests/{supervision_id}/reject/"

    def test_list_unauthenticated_returns_403(self):
        response = self.client.get(self.list_url)
        self.assertIn(response.status_code, (401, 403))

    def test_teacher_list_returns_requests(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["requests"]), 1)
        item = data["requests"][0]
        self.assertEqual(item["student_id"], self.student_person.id)
        self.assertEqual(item["student_name"], "Alice")
        self.assertEqual(item["status"], "PENDING")

    def test_teacher_can_approve_request(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.post(self._approve_url(self.supervision.id))
        self.assertEqual(response.status_code, 200)
        self.supervision.refresh_from_db()
        self.assertEqual(self.supervision.status, "APPROVED")

    def test_teacher_can_reject_request(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.post(self._reject_url(self.supervision.id))
        self.assertEqual(response.status_code, 200)
        self.supervision.refresh_from_db()
        self.assertEqual(self.supervision.status, "REJECTED")

