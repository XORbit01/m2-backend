"""Admin CRUD for Program."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from programs.models import Major, Program
from programs.serializers.admin.program import (
    AdminProgramItemSerializer,
    AdminProgramListResponseSerializer,
    AdminProgramRequestSerializer,
)


def _program_item(prog):
    return {
        "id": prog.id,
        "name": prog.name,
        "university": prog.university,
        "degree_level": prog.degree_level,
        "major_id": prog.major_id,
        "major_code": prog.major.code if prog.major else None,
    }


@extend_schema_view(
    get=extend_schema(responses={200: AdminProgramListResponseSerializer}),
    post=extend_schema(
        request=AdminProgramRequestSerializer,
        responses={201: AdminProgramItemSerializer},
    ),
)
class AdminProgramListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        programs = Program.objects.all().select_related("major").order_by("name")
        data = {"programs": [_program_item(p) for p in programs]}
        ser = AdminProgramListResponseSerializer(data=data)
        ser.is_valid(raise_exception=True)
        return Response(ser.data)

    def post(self, request):
        ser = AdminProgramRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        major_id = data.pop("major_id", None)
        if major_id is not None and not Major.objects.filter(pk=major_id).exists():
            return Response(
                {"detail": "Major not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        prog = Program.objects.create(major_id=major_id, **data)
        return Response(_program_item(prog), status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(responses={200: AdminProgramItemSerializer}),
    put=extend_schema(
        request=AdminProgramRequestSerializer,
        responses={200: AdminProgramItemSerializer},
    ),
    delete=extend_schema(responses={204: None}),
)
class AdminProgramDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, program_id):
        try:
            prog = Program.objects.select_related("major").get(pk=program_id)
        except Program.DoesNotExist:
            return Response({"detail": "Program not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(_program_item(prog))

    def put(self, request, program_id):
        try:
            prog = Program.objects.get(pk=program_id)
        except Program.DoesNotExist:
            return Response({"detail": "Program not found"}, status=status.HTTP_404_NOT_FOUND)
        ser = AdminProgramRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        major_id = data.pop("major_id", None)
        if major_id is not None and not Major.objects.filter(pk=major_id).exists():
            return Response(
                {"detail": "Major not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        prog.name = data["name"]
        prog.university = data["university"]
        prog.degree_level = data["degree_level"]
        prog.major_id = major_id
        prog.save()
        return Response(_program_item(prog))

    def delete(self, request, program_id):
        try:
            prog = Program.objects.get(pk=program_id)
        except Program.DoesNotExist:
            return Response({"detail": "Program not found"}, status=status.HTTP_404_NOT_FOUND)
        prog.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
