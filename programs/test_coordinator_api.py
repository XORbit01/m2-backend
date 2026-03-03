"""Tests for coordinator offerings, students, cohorts, and assign teacher API."""

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
    MajorCoordinator,
    Program,
    Semester,
)

User = get_user_model()


def _create_user_with_person(email, full_name="Test", password="testpass123"):
    user = User.objects.create_user(username=email, email=email, password=password)
    person = Person.objects.create(full_name=full_name, email=email, user=user)
    return user, person


class CoordinatorOfferingsListAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/programs/coordinator/offerings/"
        self.major = Major.objects.create(code="M2CS", name="Master CS")
        self.program = Program.objects.create(
            name="M2 CS", university="LU", degree_level="M2", major=self.major
        )
        self.cohort = Cohort.objects.create(
            program=self.program, academic_year="2024"
        )
        self.semester = Semester.objects.create(
            cohort=self.cohort, name="S1"
        )
        self.course = Course.objects.create(
            program=self.program, code="CS101", title="Intro"
        )

    def test_get_unauthenticated_returns_403(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, (401, 403))

    def test_get_as_coordinator_returns_offerings_for_major(self):
        coord_user, coord_person = _create_user_with_person("coord@example.com")
        MajorCoordinator.objects.create(
            major=self.major, coordinator=coord_person, is_primary=True
        )
        offering = CourseOffering.objects.create(
            course=self.course,
            cohort=self.cohort,
            semester=self.semester,
            teacher=None,
        )
        self.client.force_authenticate(user=coord_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["offerings"]), 1)
        self.assertEqual(data["offerings"][0]["id"], offering.id)
        self.assertEqual(data["offerings"][0]["course_code"], "CS101")


class CoordinatorAssignTeacherAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.major = Major.objects.create(code="M2CS", name="Master CS")
        self.program = Program.objects.create(
            name="M2 CS", university="LU", degree_level="M2", major=self.major
        )
        self.cohort = Cohort.objects.create(
            program=self.program, academic_year="2024"
        )
        self.semester = Semester.objects.create(
            cohort=self.cohort, name="S1"
        )
        self.course = Course.objects.create(
            program=self.program, code="CS101", title="Intro"
        )
        self.offering = CourseOffering.objects.create(
            course=self.course,
            cohort=self.cohort,
            semester=self.semester,
            teacher=None,
        )

    def _assign_url(self, offering_id):
        return f"/api/v1/programs/coordinator/offerings/{offering_id}/assign/"

    def test_post_assigns_teacher_when_coordinator(self):
        coord_user, coord_person = _create_user_with_person("coord@example.com")
        MajorCoordinator.objects.create(
            major=self.major, coordinator=coord_person, is_primary=True
        )
        teacher_user, teacher_person = _create_user_with_person("teacher@example.com")
        TeacherProfile.objects.create(
            person=teacher_person,
            title="Prof",
            department="CS",
            is_supervisor=False,
        )
        self.client.force_authenticate(user=coord_user)
        response = self.client.post(
            self._assign_url(self.offering.id),
            {"teacher_id": teacher_person.id},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.offering.refresh_from_db()
        self.assertEqual(self.offering.teacher_id, teacher_person.id)


class CoordinatorStudentsListAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/programs/coordinator/students/"
        self.major = Major.objects.create(code="M2CS", name="Master CS")
        self.program = Program.objects.create(
            name="M2 CS", university="LU", degree_level="M2", major=self.major
        )
        self.cohort = Cohort.objects.create(
            program=self.program, academic_year="2024"
        )

    def test_get_unauthenticated_returns_403(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, (401, 403))

    def test_get_as_coordinator_returns_students_in_major(self):
        coord_user, coord_person = _create_user_with_person("coord@example.com")
        MajorCoordinator.objects.create(
            major=self.major, coordinator=coord_person, is_primary=True
        )
        student_user, student_person = _create_user_with_person(
            "student@example.com", "Student One"
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
        self.client.force_authenticate(user=coord_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["students"]), 1)
        self.assertEqual(data["students"][0]["full_name"], "Student One")
        self.assertEqual(data["students"][0]["student_number"], "M2-001")
        self.assertEqual(data["students"][0]["cohort_academic_year"], "2024")


class CoordinatorCohortsListAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/programs/coordinator/cohorts/"
        self.major = Major.objects.create(code="M2CS", name="Master CS")
        self.program = Program.objects.create(
            name="M2 CS", university="LU", degree_level="M2", major=self.major
        )
        self.cohort = Cohort.objects.create(
            program=self.program, academic_year="2024"
        )

    def test_get_unauthenticated_returns_403(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, (401, 403))

    def test_get_as_coordinator_returns_cohorts_for_major(self):
        coord_user, coord_person = _create_user_with_person("coord@example.com")
        MajorCoordinator.objects.create(
            major=self.major, coordinator=coord_person, is_primary=True
        )
        self.client.force_authenticate(user=coord_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["cohorts"]), 1)
        self.assertEqual(data["cohorts"][0]["academic_year"], "2024")
        self.assertEqual(data["cohorts"][0]["program_name"], "M2 CS")
