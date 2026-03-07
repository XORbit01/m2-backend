"""Admin assign/remove MajorCoordinator."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Person
from programs.models import Major, MajorCoordinator
from programs.serializers.admin.major_coordinator import (
    AdminMajorCoordinatorAssignRequestSerializer,
)


@extend_schema(
    request=AdminMajorCoordinatorAssignRequestSerializer,
    responses={201: None, 200: None},
)
class AdminMajorCoordinatorAssignView(APIView):
    """POST /api/v1/programs/admin/majors/<major_id>/coordinators/"""

    permission_classes = [IsAdminUser]

    def post(self, request, major_id):
        try:
            major = Major.objects.get(pk=major_id)
        except Major.DoesNotExist:
            return Response(
                {"detail": "Major not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        ser = AdminMajorCoordinatorAssignRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        person_id = ser.validated_data["coordinator_person_id"]
        is_primary = ser.validated_data.get("is_primary", False)
        try:
            person = Person.objects.get(pk=person_id)
        except Person.DoesNotExist:
            return Response(
                {"detail": "Person not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        obj, created = MajorCoordinator.objects.get_or_create(
            major=major,
            coordinator=person,
            defaults={"is_primary": is_primary},
        )
        if not created:
            obj.is_primary = is_primary
            obj.save()
        return Response(
            {"message": "Coordinator assigned", "major_id": major.id, "person_id": person_id},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


@extend_schema(responses={204: None})
class AdminMajorCoordinatorRemoveView(APIView):
    """DELETE /api/v1/programs/admin/majors/<major_id>/coordinators/<person_id>/"""

    permission_classes = [IsAdminUser]

    def delete(self, request, major_id, person_id):
        deleted, _ = MajorCoordinator.objects.filter(
            major_id=major_id, coordinator_id=person_id
        ).delete()
        if not deleted:
            return Response(
                {"detail": "Coordinator assignment not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
