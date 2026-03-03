from core.enums import SupervisionStatus
from core.models import Person
from profiles.models import TeacherProfile
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from supervision.models import Supervision
from supervision.serializers.teacher.action_response import (
    TeacherSupervisionActionResponseSerializer,
)
from supervision.serializers.teacher.list_response import (
    TeacherSupervisionListResponseSerializer,
)


class TeacherSupervisionListView(APIView):
    """
    GET /api/v1/supervision/teacher/requests/
    List supervision requests for the authenticated teacher.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            person = request.user.person
        except Person.DoesNotExist:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not TeacherProfile.objects.filter(person=person).exists():
            return Response(
                {"detail": "User is not a teacher"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        supervisions = (
            Supervision.objects.filter(teacher=person)
            .select_related("student")
            .order_by("-created_at")
        )
        items = [
            {
                "id": s.id,
                "student_id": s.student_id,
                "student_name": s.student.full_name,
                "student_email": s.student.email,
                "status": s.status,
            }
            for s in supervisions
        ]
        data = {"requests": items}
        serializer = TeacherSupervisionListResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class TeacherSupervisionApproveView(APIView):
    """
    POST /api/v1/supervision/teacher/requests/<supervision_id>/approve/
    Approve a supervision request for the authenticated teacher.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, supervision_id):
        try:
            person = request.user.person
        except Person.DoesNotExist:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not TeacherProfile.objects.filter(person=person).exists():
            return Response(
                {"detail": "User is not a teacher"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            supervision = Supervision.objects.select_related("teacher").get(
                pk=supervision_id,
                teacher=person,
            )
        except Supervision.DoesNotExist:
            return Response(
                {"detail": "Supervision request not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if supervision.status == SupervisionStatus.APPROVED:
            return Response(
                {"detail": "Supervision already approved"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if supervision.status == SupervisionStatus.REJECTED:
            return Response(
                {"detail": "Supervision already rejected"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        supervision.status = SupervisionStatus.APPROVED
        supervision.save(update_fields=["status", "updated_at"])

        resp = TeacherSupervisionActionResponseSerializer(
            {"message": "Supervision approved"}
        )
        return Response(resp.data)


class TeacherSupervisionRejectView(APIView):
    """
    POST /api/v1/supervision/teacher/requests/<supervision_id>/reject/
    Reject a supervision request for the authenticated teacher.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, supervision_id):
        try:
            person = request.user.person
        except Person.DoesNotExist:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not TeacherProfile.objects.filter(person=person).exists():
            return Response(
                {"detail": "User is not a teacher"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            supervision = Supervision.objects.select_related("teacher").get(
                pk=supervision_id,
                teacher=person,
            )
        except Supervision.DoesNotExist:
            return Response(
                {"detail": "Supervision request not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if supervision.status == SupervisionStatus.REJECTED:
            return Response(
                {"detail": "Supervision already rejected"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if supervision.status == SupervisionStatus.APPROVED:
            return Response(
                {"detail": "Supervision already approved"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        supervision.status = SupervisionStatus.REJECTED
        supervision.save(update_fields=["status", "updated_at"])

        resp = TeacherSupervisionActionResponseSerializer(
            {"message": "Supervision rejected"}
        )
        return Response(resp.data)

