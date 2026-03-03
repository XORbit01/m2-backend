from core.enums import SupervisionStatus
from core.models import Person
from profiles.models import StudentProfile, TeacherProfile
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from supervision.models import Supervision
from supervision.serializers.student.create_request import (
    StudentCreateSupervisionRequestSerializer,
)
from supervision.serializers.student.create_response import (
    StudentCreateSupervisionResponseSerializer,
)
from supervision.serializers.student.list_response import (
    StudentSupervisionListResponseSerializer,
)
from supervision.serializers.student.action_response import (
    StudentSupervisionActionResponseSerializer,
)


class StudentSupervisionListCreateView(APIView):
    """
    GET /api/v1/supervision/student/requests/
    List supervision requests for the authenticated student.

    POST /api/v1/supervision/student/requests/
    Create a new supervision request for the authenticated student.
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

        if not StudentProfile.objects.filter(person=person).exists():
            return Response(
                {"detail": "User is not a student"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        supervisions = (
            Supervision.objects.filter(student=person)
            .select_related("teacher")
            .order_by("-created_at")
        )
        items = [
            {
                "id": s.id,
                "teacher_id": s.teacher_id,
                "teacher_name": s.teacher.full_name,
                "teacher_email": s.teacher.email,
                "status": s.status,
            }
            for s in supervisions
        ]
        data = {"supervisions": items}
        serializer = StudentSupervisionListResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            person = request.user.person
        except Person.DoesNotExist:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not StudentProfile.objects.filter(person=person).exists():
            return Response(
                {"detail": "User is not a student"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        req = StudentCreateSupervisionRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        teacher_id = req.validated_data["teacher_id"]

        try:
            teacher_person = Person.objects.get(pk=teacher_id)
        except Person.DoesNotExist:
            return Response(
                {"detail": "Teacher (person) not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            teacher_profile = TeacherProfile.objects.get(person=teacher_person)
        except TeacherProfile.DoesNotExist:
            return Response(
                {"detail": "Person is not a teacher"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not teacher_profile.is_supervisor:
            return Response(
                {"detail": "Teacher is not available as supervisor"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        supervision, created = Supervision.objects.get_or_create(
            student=person,
            teacher=teacher_person,
        )
        if not created and supervision.status == SupervisionStatus.PENDING:
            return Response(
                {"detail": "Supervision request already pending"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not created and supervision.status == SupervisionStatus.APPROVED:
            return Response(
                {"detail": "Teacher is already your supervisor"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not created and supervision.status == SupervisionStatus.REJECTED:
            supervision.status = SupervisionStatus.PENDING
            supervision.save(update_fields=["status", "updated_at"])

        resp = StudentCreateSupervisionResponseSerializer(
            {
                "id": supervision.id,
                "teacher_id": teacher_person.id,
                "status": supervision.status,
            }
        )
        return Response(resp.data, status=status.HTTP_201_CREATED)


class StudentSupervisionCancelView(APIView):
    """
    POST /api/v1/supervision/student/requests/<supervision_id>/cancel/
    Cancel a pending supervision request for the authenticated student.
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

        if not StudentProfile.objects.filter(person=person).exists():
            return Response(
                {"detail": "User is not a student"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            supervision = Supervision.objects.get(
                pk=supervision_id,
                student=person,
            )
        except Supervision.DoesNotExist:
            return Response(
                {"detail": "Supervision request not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if supervision.status != SupervisionStatus.PENDING:
            return Response(
                {"detail": "Only pending requests can be cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        supervision.delete()

        resp = StudentSupervisionActionResponseSerializer(
            {"message": "Supervision request cancelled"}
        )
        return Response(resp.data)

