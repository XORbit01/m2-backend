"""Admin CRUD for Course."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from programs.models import Course, Program
from programs.serializers.admin.course import (
    AdminCourseItemSerializer,
    AdminCourseListResponseSerializer,
    AdminCourseRequestSerializer,
)


def _course_item(c):
    return {
        "id": c.id,
        "program_id": c.program_id,
        "program_name": c.program.name,
        "code": c.code,
        "title": c.title,
        "major_id": c.program.major_id,
        "major_code": c.program.major.code if c.program.major else None,
    }


@extend_schema_view(
    get=extend_schema(responses={200: AdminCourseListResponseSerializer}),
    post=extend_schema(
        request=AdminCourseRequestSerializer,
        responses={201: AdminCourseItemSerializer},
    ),
)
class AdminCourseListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        courses = Course.objects.select_related("program", "program__major").order_by(
            "program__name", "code"
        )
        data = {"courses": [_course_item(c) for c in courses]}
        ser = AdminCourseListResponseSerializer(data=data)
        ser.is_valid(raise_exception=True)
        return Response(ser.data)

    def post(self, request):
        ser = AdminCourseRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        program_id = ser.validated_data["program_id"]
        if not Program.objects.filter(pk=program_id).exists():
            return Response(
                {"detail": "Program not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        code = ser.validated_data["code"]
        if Course.objects.filter(program_id=program_id, code=code).exists():
            return Response(
                {"detail": "Course with this code already exists in program"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        course = Course.objects.create(**ser.validated_data)
        course.refresh_from_db()
        c = Course.objects.select_related("program", "program__major").get(pk=course.id)
        return Response(_course_item(c), status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(responses={200: AdminCourseItemSerializer}),
    put=extend_schema(
        request=AdminCourseRequestSerializer,
        responses={200: AdminCourseItemSerializer},
    ),
    delete=extend_schema(responses={204: None}),
)
class AdminCourseDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, course_id):
        try:
            c = Course.objects.select_related("program", "program__major").get(pk=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(_course_item(c))

    def put(self, request, course_id):
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        ser = AdminCourseRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        program_id = ser.validated_data["program_id"]
        if not Program.objects.filter(pk=program_id).exists():
            return Response(
                {"detail": "Program not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        code = ser.validated_data["code"]
        if Course.objects.filter(program_id=program_id, code=code).exclude(pk=course_id).exists():
            return Response(
                {"detail": "Course with this code already exists in program"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        course.program_id = program_id
        course.code = code
        course.title = ser.validated_data["title"]
        course.save()
        c = Course.objects.select_related("program", "program__major").get(pk=course.id)
        return Response(_course_item(c))

    def delete(self, request, course_id):
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
