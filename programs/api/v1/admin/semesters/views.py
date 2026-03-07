"""Admin CRUD for Semester."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from programs.models import Cohort, Semester
from programs.serializers.admin.semester import (
    AdminSemesterItemSerializer,
    AdminSemesterListResponseSerializer,
    AdminSemesterRequestSerializer,
)


def _semester_item(s):
    return {
        "id": s.id,
        "cohort_id": s.cohort_id,
        "cohort_academic_year": s.cohort.academic_year,
        "program_name": s.cohort.program.name,
        "name": s.name,
    }


@extend_schema_view(
    get=extend_schema(responses={200: AdminSemesterListResponseSerializer}),
    post=extend_schema(
        request=AdminSemesterRequestSerializer,
        responses={201: AdminSemesterItemSerializer},
    ),
)
class AdminSemesterListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        semesters = Semester.objects.select_related("cohort", "cohort__program").order_by(
            "cohort__academic_year", "name"
        )
        data = {"semesters": [_semester_item(s) for s in semesters]}
        ser = AdminSemesterListResponseSerializer(data=data)
        ser.is_valid(raise_exception=True)
        return Response(ser.data)

    def post(self, request):
        ser = AdminSemesterRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        cohort_id = ser.validated_data["cohort_id"]
        if not Cohort.objects.filter(pk=cohort_id).exists():
            return Response(
                {"detail": "Cohort not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        name = ser.validated_data["name"]
        if Semester.objects.filter(cohort_id=cohort_id, name=name).exists():
            return Response(
                {"detail": "Semester with this name already exists in cohort"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        semester = Semester.objects.create(**ser.validated_data)
        semester.refresh_from_db()
        s = Semester.objects.select_related("cohort", "cohort__program").get(pk=semester.id)
        return Response(_semester_item(s), status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(responses={200: AdminSemesterItemSerializer}),
    put=extend_schema(
        request=AdminSemesterRequestSerializer,
        responses={200: AdminSemesterItemSerializer},
    ),
    delete=extend_schema(responses={204: None}),
)
class AdminSemesterDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, semester_id):
        try:
            s = Semester.objects.select_related("cohort", "cohort__program").get(pk=semester_id)
        except Semester.DoesNotExist:
            return Response({"detail": "Semester not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(_semester_item(s))

    def put(self, request, semester_id):
        try:
            semester = Semester.objects.get(pk=semester_id)
        except Semester.DoesNotExist:
            return Response({"detail": "Semester not found"}, status=status.HTTP_404_NOT_FOUND)
        ser = AdminSemesterRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        cohort_id = ser.validated_data["cohort_id"]
        if not Cohort.objects.filter(pk=cohort_id).exists():
            return Response(
                {"detail": "Cohort not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        name = ser.validated_data["name"]
        if Semester.objects.filter(cohort_id=cohort_id, name=name).exclude(pk=semester_id).exists():
            return Response(
                {"detail": "Semester with this name already exists in cohort"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        semester.cohort_id = cohort_id
        semester.name = name
        semester.save()
        s = Semester.objects.select_related("cohort", "cohort__program").get(pk=semester.id)
        return Response(_semester_item(s))

    def delete(self, request, semester_id):
        try:
            semester = Semester.objects.get(pk=semester_id)
        except Semester.DoesNotExist:
            return Response({"detail": "Semester not found"}, status=status.HTTP_404_NOT_FOUND)
        semester.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
