"""Admin CRUD for Cohort."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from programs.models import Cohort, Program
from programs.serializers.admin.cohort import (
    AdminCohortItemSerializer,
    AdminCohortListResponseSerializer,
    AdminCohortRequestSerializer,
)


def _cohort_item(c):
    return {
        "id": c.id,
        "program_id": c.program_id,
        "program_name": c.program.name,
        "academic_year": c.academic_year,
        "major_id": c.program.major_id,
        "major_code": c.program.major.code if c.program.major else None,
    }


@extend_schema_view(
    get=extend_schema(responses={200: AdminCohortListResponseSerializer}),
    post=extend_schema(
        request=AdminCohortRequestSerializer,
        responses={201: AdminCohortItemSerializer},
    ),
)
class AdminCohortListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        cohorts = Cohort.objects.select_related("program", "program__major").order_by(
            "-academic_year", "program__name"
        )
        data = {"cohorts": [_cohort_item(c) for c in cohorts]}
        ser = AdminCohortListResponseSerializer(data=data)
        ser.is_valid(raise_exception=True)
        return Response(ser.data)

    def post(self, request):
        ser = AdminCohortRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        program_id = ser.validated_data["program_id"]
        try:
            Program.objects.get(pk=program_id)
        except Program.DoesNotExist:
            return Response(
                {"detail": "Program not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cohort = Cohort.objects.create(**ser.validated_data)
        cohort.refresh_from_db()
        cohort = Cohort.objects.select_related("program", "program__major").get(pk=cohort.id)
        return Response(_cohort_item(cohort), status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(responses={200: AdminCohortItemSerializer}),
    put=extend_schema(
        request=AdminCohortRequestSerializer,
        responses={200: AdminCohortItemSerializer},
    ),
    delete=extend_schema(responses={204: None}),
)
class AdminCohortDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, cohort_id):
        try:
            c = Cohort.objects.select_related("program", "program__major").get(pk=cohort_id)
        except Cohort.DoesNotExist:
            return Response({"detail": "Cohort not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(_cohort_item(c))

    def put(self, request, cohort_id):
        try:
            cohort = Cohort.objects.get(pk=cohort_id)
        except Cohort.DoesNotExist:
            return Response({"detail": "Cohort not found"}, status=status.HTTP_404_NOT_FOUND)
        ser = AdminCohortRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        program_id = ser.validated_data["program_id"]
        if not Program.objects.filter(pk=program_id).exists():
            return Response(
                {"detail": "Program not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cohort.program_id = program_id
        cohort.academic_year = ser.validated_data["academic_year"]
        cohort.save()
        cohort.refresh_from_db()
        c = Cohort.objects.select_related("program", "program__major").get(pk=cohort.id)
        return Response(_cohort_item(c))

    def delete(self, request, cohort_id):
        try:
            cohort = Cohort.objects.get(pk=cohort_id)
        except Cohort.DoesNotExist:
            return Response({"detail": "Cohort not found"}, status=status.HTTP_404_NOT_FOUND)
        cohort.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
