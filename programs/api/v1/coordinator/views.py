from core.models import Person
from enrollment.models import Enrollment
from profiles.models import StudentProfile, TeacherProfile

from programs.helpers.coordinator import get_coordinated_major_ids
from programs.models import Cohort, CourseOffering
from programs.serializers.coordinator.assign_teacher_request import (
    CoordinatorAssignTeacherRequestSerializer,
)
from programs.serializers.coordinator.assign_teacher_response import (
    CoordinatorAssignTeacherResponseSerializer,
)
from programs.serializers.coordinator.cohorts_list_response import (
    CoordinatorCohortsListResponseSerializer,
)
from programs.serializers.coordinator.offerings_list_response import (
    CoordinatorOfferingsListResponseSerializer,
)
from programs.serializers.coordinator.students_list_response import (
    CoordinatorStudentsListResponseSerializer,
)
from programs.serializers.coordinator.teachers_list_response import (
    CoordinatorTeachersListResponseSerializer,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


def _get_coordinator_person(request):
    try:
        return request.user.person
    except Person.DoesNotExist:
        return None


def _can_coordinator_manage_offering(person, offering):
    """True if offering's course belongs to a program in coordinator's major(s)."""
    if person is None or offering is None:
        return False
    program = offering.course.program
    if program.major_id is None:
        return False
    major_ids = get_coordinated_major_ids(person)
    return program.major_id in major_ids


class CoordinatorOfferingsListView(APIView):
    """
    GET /api/v1/programs/coordinator/offerings/
    Returns course offerings for programs in the coordinator's major(s).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        person = _get_coordinator_person(request)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )
        major_ids = list(get_coordinated_major_ids(person))
        if not major_ids:
            resp = CoordinatorOfferingsListResponseSerializer({"offerings": []})
            return Response(resp.data)

        offerings = (
            CourseOffering.objects.filter(course__program__major_id__in=major_ids)
            .select_related("course", "cohort", "semester", "teacher")
            .order_by("-cohort__academic_year", "semester__name", "course__code")
        )
        items = [
            {
                "id": o.id,
                "course_id": o.course_id,
                "course_code": o.course.code,
                "course_title": o.course.title,
                "cohort_id": o.cohort_id,
                "cohort_academic_year": o.cohort.academic_year,
                "semester_id": o.semester_id,
                "semester_name": o.semester.name,
                "teacher_id": o.teacher_id,
                "teacher_name": o.teacher.full_name if o.teacher else None,
            }
            for o in offerings
        ]
        data = {"offerings": items}
        serializer = CoordinatorOfferingsListResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class CoordinatorAssignTeacherView(APIView):
    """
    POST /api/v1/programs/coordinator/offerings/<offering_id>/assign/
    Assign teacher to a course offering. Coordinator must manage that major.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, offering_id):
        person = _get_coordinator_person(request)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )
        req = CoordinatorAssignTeacherRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        teacher_id = req.validated_data["teacher_id"]

        try:
            offering = CourseOffering.objects.select_related(
                "course__program"
            ).get(pk=offering_id)
        except CourseOffering.DoesNotExist:
            return Response(
                {"detail": "Offering not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not _can_coordinator_manage_offering(person, offering):
            return Response(
                {"detail": "Not allowed to manage this offering"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            teacher_person = Person.objects.get(pk=teacher_id)
        except Person.DoesNotExist:
            return Response(
                {"detail": "Teacher (person) not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not TeacherProfile.objects.filter(person=teacher_person).exists():
            return Response(
                {"detail": "Person is not a teacher"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        offering.teacher = teacher_person
        offering.save(update_fields=["teacher"])

        resp = CoordinatorAssignTeacherResponseSerializer(
            {"message": "Teacher assigned"}
        )
        return Response(resp.data)


class CoordinatorTeachersListView(APIView):
    """
    GET /api/v1/programs/coordinator/teachers/
    Returns all teachers (for coordinator to choose when assigning).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        person = _get_coordinator_person(request)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )
        teachers = (
            TeacherProfile.objects.select_related("person")
            .order_by("person__full_name")
        )
        items = [
            {
                "person_id": t.person_id,
                "full_name": t.person.full_name,
                "email": t.person.email,
                "title": t.title,
                "department": t.department,
                "is_supervisor": t.is_supervisor,
            }
            for t in teachers
        ]
        data = {"teachers": items}
        serializer = CoordinatorTeachersListResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class CoordinatorStudentsListView(APIView):
    """
    GET /api/v1/programs/coordinator/students/
    Returns students enrolled in coordinator's major(s).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        person = _get_coordinator_person(request)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )
        major_ids = list(get_coordinated_major_ids(person))
        if not major_ids:
            resp = CoordinatorStudentsListResponseSerializer({"students": []})
            return Response(resp.data)

        enrollments = (
            Enrollment.objects.filter(major_id__in=major_ids)
            .select_related("student", "cohort", "major", "cohort__program")
            .prefetch_related("student__student_profile")
            .order_by("-cohort__academic_year", "student__full_name")
        )
        items = []
        for e in enrollments:
            student_number = ""
            try:
                student_number = e.student.student_profile.student_number
            except StudentProfile.DoesNotExist:
                pass
            items.append(
                {
                    "person_id": e.student_id,
                    "full_name": e.student.full_name,
                    "email": e.student.email,
                    "student_number": student_number,
                    "enrollment_id": e.id,
                    "cohort_id": e.cohort_id,
                    "cohort_academic_year": e.cohort.academic_year,
                    "major_id": e.major_id,
                    "major_code": e.major.code,
                    "enrollment_status": e.status,
                }
            )
        data = {"students": items}
        serializer = CoordinatorStudentsListResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class CoordinatorCohortsListView(APIView):
    """
    GET /api/v1/programs/coordinator/cohorts/
    Returns cohorts for programs in coordinator's major(s).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        person = _get_coordinator_person(request)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )
        major_ids = list(get_coordinated_major_ids(person))
        if not major_ids:
            resp = CoordinatorCohortsListResponseSerializer({"cohorts": []})
            return Response(resp.data)

        cohorts = (
            Cohort.objects.filter(program__major_id__in=major_ids)
            .select_related("program", "program__major")
            .order_by("-academic_year", "program__name")
        )
        items = [
            {
                "id": c.id,
                "academic_year": c.academic_year,
                "program_id": c.program_id,
                "program_name": c.program.name,
                "major_id": c.program.major_id,
                "major_code": c.program.major.code if c.program.major else None,
            }
            for c in cohorts
        ]
        data = {"cohorts": items}
        serializer = CoordinatorCohortsListResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
