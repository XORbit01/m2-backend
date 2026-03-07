"""Admin CRUD for Major."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from programs.models import Major
from programs.serializers.admin.major import (
    AdminMajorItemSerializer,
    AdminMajorListResponseSerializer,
    AdminMajorRequestSerializer,
)


def _major_item(major):
    return {"id": major.id, "code": major.code, "name": major.name}


@extend_schema_view(
    get=extend_schema(responses={200: AdminMajorListResponseSerializer}),
    post=extend_schema(
        request=AdminMajorRequestSerializer,
        responses={201: AdminMajorItemSerializer},
    ),
)
class AdminMajorListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        majors = Major.objects.all().order_by("code")
        data = {"majors": [_major_item(m) for m in majors]}
        ser = AdminMajorListResponseSerializer(data=data)
        ser.is_valid(raise_exception=True)
        return Response(ser.data)

    def post(self, request):
        ser = AdminMajorRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        code = ser.validated_data["code"]
        if Major.objects.filter(code=code).exists():
            return Response(
                {"detail": "Major with this code already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        major = Major.objects.create(**ser.validated_data)
        return Response(_major_item(major), status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(responses={200: AdminMajorItemSerializer}),
    put=extend_schema(
        request=AdminMajorRequestSerializer,
        responses={200: AdminMajorItemSerializer},
    ),
    delete=extend_schema(responses={204: None}),
)
class AdminMajorDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, major_id):
        try:
            major = Major.objects.get(pk=major_id)
        except Major.DoesNotExist:
            return Response({"detail": "Major not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(_major_item(major))

    def put(self, request, major_id):
        try:
            major = Major.objects.get(pk=major_id)
        except Major.DoesNotExist:
            return Response({"detail": "Major not found"}, status=status.HTTP_404_NOT_FOUND)
        ser = AdminMajorRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        code = ser.validated_data["code"]
        if Major.objects.filter(code=code).exclude(pk=major_id).exists():
            return Response(
                {"detail": "Major with this code already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        major.code = ser.validated_data["code"]
        major.name = ser.validated_data["name"]
        major.save()
        return Response(_major_item(major))

    def delete(self, request, major_id):
        try:
            major = Major.objects.get(pk=major_id)
        except Major.DoesNotExist:
            return Response({"detail": "Major not found"}, status=status.HTTP_404_NOT_FOUND)
        major.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
