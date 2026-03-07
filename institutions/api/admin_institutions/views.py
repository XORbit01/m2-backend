"""Admin CRUD for Institution."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from institutions.models import Institution
from institutions.serializers.admin_institution import (
    AdminInstitutionItemSerializer,
    AdminInstitutionListResponseSerializer,
    AdminInstitutionRequestSerializer,
)


def _institution_item(i):
    return {
        "id": i.id,
        "name": i.name,
        "country": i.country,
        "type": i.type,
        "website": i.website or "",
    }


@extend_schema_view(
    get=extend_schema(responses={200: AdminInstitutionListResponseSerializer}),
    post=extend_schema(
        request=AdminInstitutionRequestSerializer,
        responses={201: AdminInstitutionItemSerializer},
    ),
)
class AdminInstitutionListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        institutions = Institution.objects.all().order_by("name")
        data = {"institutions": [_institution_item(i) for i in institutions]}
        ser = AdminInstitutionListResponseSerializer(data=data)
        ser.is_valid(raise_exception=True)
        return Response(ser.data)

    def post(self, request):
        ser = AdminInstitutionRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        name = ser.validated_data["name"]
        if Institution.objects.filter(name=name).exists():
            return Response(
                {"detail": "Institution with this name already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        inst = Institution.objects.create(**ser.validated_data)
        return Response(_institution_item(inst), status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(responses={200: AdminInstitutionItemSerializer}),
    put=extend_schema(
        request=AdminInstitutionRequestSerializer,
        responses={200: AdminInstitutionItemSerializer},
    ),
    delete=extend_schema(responses={204: None}),
)
class AdminInstitutionDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, institution_id):
        try:
            inst = Institution.objects.get(pk=institution_id)
        except Institution.DoesNotExist:
            return Response(
                {"detail": "Institution not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(_institution_item(inst))

    def put(self, request, institution_id):
        try:
            inst = Institution.objects.get(pk=institution_id)
        except Institution.DoesNotExist:
            return Response(
                {"detail": "Institution not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        ser = AdminInstitutionRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        name = ser.validated_data["name"]
        if Institution.objects.filter(name=name).exclude(pk=institution_id).exists():
            return Response(
                {"detail": "Institution with this name already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        inst.name = ser.validated_data["name"]
        inst.country = ser.validated_data["country"]
        inst.type = ser.validated_data["type"]
        inst.website = ser.validated_data.get("website", "") or ""
        inst.save()
        return Response(_institution_item(inst))

    def delete(self, request, institution_id):
        try:
            inst = Institution.objects.get(pk=institution_id)
        except Institution.DoesNotExist:
            return Response(
                {"detail": "Institution not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        inst.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
