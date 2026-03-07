"""Admin CRUD for CourseOffering."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Person
from programs.models import Cohort, Course, CourseOffering, Semester
from programs.serializers.admin.offering import (
    AdminOfferingItemSerializer,
    AdminOfferingListResponseSerializer,
    AdminOfferingRequestSerializer,
)


def _offering_item(o):
    return {
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


@extend_schema_view(
    get=extend_schema(responses={200: AdminOfferingListResponseSerializer}),
    post=extend_schema(
        request=AdminOfferingRequestSerializer,
        responses={201: AdminOfferingItemSerializer},
    ),
)
class AdminOfferingListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        offerings = (
            CourseOffering.objects.select_related(
                "course", "cohort", "semester", "teacher"
            )
            .order_by("-cohort__academic_year", "semester__name", "course__code")
        )
        data = {"offerings": [_offering_item(o) for o in offerings]}
        ser = AdminOfferingListResponseSerializer(data=data)
        ser.is_valid(raise_exception=True)
        return Response(ser.data)

    def post(self, request):
        ser = AdminOfferingRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        course_id = ser.validated_data["course_id"]
        cohort_id = ser.validated_data["cohort_id"]
        semester_id = ser.validated_data["semester_id"]
        teacher_id = ser.validated_data.get("teacher_id")

        if not Course.objects.filter(pk=course_id).exists():
            return Response(
                {"detail": "Course not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not Cohort.objects.filter(pk=cohort_id).exists():
            return Response(
                {"detail": "Cohort not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        semester = Semester.objects.filter(pk=semester_id).first()
        if not semester:
            return Response(
                {"detail": "Semester not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if semester.cohort_id != cohort_id:
            return Response(
                {"detail": "Semester does not belong to cohort"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if teacher_id is not None and not Person.objects.filter(pk=teacher_id).exists():
            return Response(
                {"detail": "Teacher (person) not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if CourseOffering.objects.filter(
            course_id=course_id, cohort_id=cohort_id, semester_id=semester_id
        ).exists():
            return Response(
                {"detail": "Offering already exists for this course/cohort/semester"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        offering = CourseOffering.objects.create(
            course_id=course_id,
            cohort_id=cohort_id,
            semester_id=semester_id,
            teacher_id=teacher_id,
        )
        offering.refresh_from_db()
        o = CourseOffering.objects.select_related(
            "course", "cohort", "semester", "teacher"
        ).get(pk=offering.id)
        return Response(_offering_item(o), status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(responses={200: AdminOfferingItemSerializer}),
    put=extend_schema(
        request=AdminOfferingRequestSerializer,
        responses={200: AdminOfferingItemSerializer},
    ),
    delete=extend_schema(responses={204: None}),
)
class AdminOfferingDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, offering_id):
        try:
            o = CourseOffering.objects.select_related(
                "course", "cohort", "semester", "teacher"
            ).get(pk=offering_id)
        except CourseOffering.DoesNotExist:
            return Response({"detail": "Offering not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(_offering_item(o))

    def put(self, request, offering_id):
        try:
            offering = CourseOffering.objects.get(pk=offering_id)
        except CourseOffering.DoesNotExist:
            return Response({"detail": "Offering not found"}, status=status.HTTP_404_NOT_FOUND)
        ser = AdminOfferingRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        course_id = ser.validated_data["course_id"]
        cohort_id = ser.validated_data["cohort_id"]
        semester_id = ser.validated_data["semester_id"]
        teacher_id = ser.validated_data.get("teacher_id")

        if not Course.objects.filter(pk=course_id).exists():
            return Response({"detail": "Course not found"}, status=status.HTTP_400_BAD_REQUEST)
        if not Cohort.objects.filter(pk=cohort_id).exists():
            return Response({"detail": "Cohort not found"}, status=status.HTTP_400_BAD_REQUEST)
        semester = Semester.objects.filter(pk=semester_id).first()
        if not semester or semester.cohort_id != cohort_id:
            return Response(
                {"detail": "Semester not found or does not belong to cohort"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if teacher_id is not None and not Person.objects.filter(pk=teacher_id).exists():
            return Response(
                {"detail": "Teacher (person) not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if CourseOffering.objects.filter(
            course_id=course_id, cohort_id=cohort_id, semester_id=semester_id
        ).exclude(pk=offering_id).exists():
            return Response(
                {"detail": "Offering already exists for this course/cohort/semester"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        offering.course_id = course_id
        offering.cohort_id = cohort_id
        offering.semester_id = semester_id
        offering.teacher_id = teacher_id
        offering.save()
        o = CourseOffering.objects.select_related(
            "course", "cohort", "semester", "teacher"
        ).get(pk=offering.id)
        return Response(_offering_item(o))

    def delete(self, request, offering_id):
        try:
            offering = CourseOffering.objects.get(pk=offering_id)
        except CourseOffering.DoesNotExist:
            return Response({"detail": "Offering not found"}, status=status.HTTP_404_NOT_FOUND)
        offering.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
