from core.models import Person
from enrollment.models import Enrollment
from profiles.models import StudentProfile

from programs.models import CourseOffering
from programs.serializers.teacher.course_students_response import (
    TeacherCourseStudentsResponseSerializer,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


def _get_teacher_person(request):
    try:
        return request.user.person
    except Person.DoesNotExist:
        return None


class TeacherCourseStudentsListView(APIView):
    """
    GET /api/v1/programs/teacher/courses/<offering_id>/students/
    Returns students enrolled in the course offering's cohort.
    Teacher must be assigned to that offering.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, offering_id):
        person = _get_teacher_person(request)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            offering = CourseOffering.objects.select_related("cohort").get(
                pk=offering_id
            )
        except CourseOffering.DoesNotExist:
            return Response(
                {"detail": "Offering not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if offering.teacher_id != person.id:
            return Response(
                {"detail": "Not assigned to this course offering"},
                status=status.HTTP_403_FORBIDDEN,
            )

        enrollments = (
            Enrollment.objects.filter(cohort_id=offering.cohort_id)
            .select_related("student")
            .prefetch_related("student__student_profile")
            .order_by("student__full_name")
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
                }
            )
        data = {"students": items}
        serializer = TeacherCourseStudentsResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
