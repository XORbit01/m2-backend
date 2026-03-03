"""Tests for teacher course students API."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Person
from enrollment.models import Enrollment
from profiles.models import StudentProfile, TeacherProfile
from programs.models import (
    Cohort,
    Course,
    CourseOffering,
    Major,
    Program,
    Semester,
)

User = get_user_model()


def _create_user_with_person(email, full_name="Test", password="testpass123"):
    user = User.objects.create_user(username=email, email=email, password=password)
    person = Person.objects.create(full_name=full_name, email=email, user=user)
    return user, person


class TeacherCourseStudentsListAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.major = Major.objects.create(code="M2CS", name="Master CS")
        self.program = Program.objects.create(
            name="M2 CS", university="LU", degree_level="M2", major=self.major
        )
        self.cohort = Cohort.objects.create(
            program=self.program, academic_year="2024"
        )
        self.semester = Semester.objects.create(cohort=self.cohort, name="S1")
        self.course = Course.objects.create(
            program=self.program, code="CS101", title="Intro"
        )
        self.teacher_user, self.teacher_person = _create_user_with_person(
            "teacher@example.com", "Dr. Smith"
        )
        TeacherProfile.objects.create(
            person=self.teacher_person,
            title="Professor",
            department="CS",
            is_supervisor=False,
        )
        self.offering = CourseOffering.objects.create(
            course=self.course,
            cohort=self.cohort,
            semester=self.semester,
            teacher=self.teacher_person,
        )

    def _students_url(self, offering_id):
        return f"/api/v1/programs/teacher/courses/{offering_id}/students/"

    def test_get_unauthenticated_returns_403(self):
        response = self.client.get(self._students_url(self.offering.id))
        self.assertIn(response.status_code, (401, 403))

    def test_get_as_assigned_teacher_returns_students(self):
        student_user, student_person = _create_user_with_person(
            "student@example.com", "Alice"
        )
        StudentProfile.objects.create(
            person=student_person, student_number="M2-001", current_status="ACTIVE"
        )
        Enrollment.objects.create(
            student=student_person,
            cohort=self.cohort,
            major=self.major,
            status="ACTIVE",
        )
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get(self._students_url(self.offering.id))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["students"]), 1)
        self.assertEqual(data["students"][0]["full_name"], "Alice")
        self.assertEqual(data["students"][0]["student_number"], "M2-001")

    def test_get_offering_not_found_returns_404(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get(self._students_url(99999))
        self.assertEqual(response.status_code, 404)

    def test_get_as_non_assigned_teacher_returns_403(self):
        other_teacher_user, other_teacher_person = _create_user_with_person(
            "other@example.com"
        )
        TeacherProfile.objects.create(
            person=other_teacher_person,
            title="Prof",
            department="CS",
            is_supervisor=False,
        )
        self.client.force_authenticate(user=other_teacher_user)
        response = self.client.get(self._students_url(self.offering.id))
        self.assertEqual(response.status_code, 403)
