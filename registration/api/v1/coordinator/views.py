import logging

from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Person
from registration.enums import RegistrationStatus
from registration.helpers.coordinator import (can_coordinator_verify_session,
                                              get_coordinated_major_ids)
from registration.helpers.profile_creation import \
    create_profiles_from_accepted_session
from registration.models import RegistrationSession
from registration.serializers.coordinator.accept_response import \
    CoordinatorAcceptResponseSerializer
from registration.serializers.coordinator.pending_list_response import \
    CoordinatorPendingListResponseSerializer
from registration.serializers.coordinator.reject_response import \
    CoordinatorRejectResponseSerializer

log = logging.getLogger(__name__)


def _get_coordinator_person(request):
    """Return request.user.person or None; 403 if no person."""
    try:
        return request.user.person
    except Person.DoesNotExist:
        return None


@extend_schema(responses={200: CoordinatorPendingListResponseSerializer})
class CoordinatorPendingListView(APIView):
    """
    GET /api/v1/registration/coordinator/pending/
    Requires auth. Returns submitted registrations for majors the current user coordinates.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        person = _get_coordinator_person(request)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )
        major_ids = list(get_coordinated_major_ids(person))
        if not major_ids:
            resp = CoordinatorPendingListResponseSerializer({"sessions": []})
            return Response(resp.data)

        q = Q(status=RegistrationStatus.SUBMITTED.value) & (
            Q(payload__student__major_id__in=major_ids)
            | Q(payload__alumni__major_id__in=major_ids)
        )
        sessions = (
            RegistrationSession.objects.filter(q)
            .select_related("person")
            .order_by("-created_at")
        )
        items = [
            {
                "session_id": s.id,
                "person_id": s.person_id,
                "full_name": s.person.full_name,
                "email": s.person.email,
                "base_role": s.base_role,
                "payload": s.payload,
                "created_at": s.created_at,
            }
            for s in sessions
        ]
        data = {"sessions": items}
        serializer = CoordinatorPendingListResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


@extend_schema(request=None, responses={200: CoordinatorAcceptResponseSerializer})
class CoordinatorAcceptView(APIView):
    """
    POST /api/v1/registration/coordinator/<session_id>/accept/
    Requires auth. Coordinator for the session's major can accept (final stage).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        person = _get_coordinator_person(request)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            session = RegistrationSession.objects.get(pk=session_id)
        except RegistrationSession.DoesNotExist:
            return Response(
                {"detail": "Session not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not can_coordinator_verify_session(person, session):
            return Response(
                {"detail": "Not allowed to verify this session"},
                status=status.HTTP_403_FORBIDDEN,
            )
        session.status = RegistrationStatus.ACCEPTED.value
        session.save(update_fields=["status", "updated_at"])
        create_profiles_from_accepted_session(session)
        resp = CoordinatorAcceptResponseSerializer(
            {"status": session.status, "message": "Registration accepted"}
        )
        return Response(resp.data)


@extend_schema(request=None, responses={200: CoordinatorRejectResponseSerializer})
class CoordinatorRejectView(APIView):
    """
    POST /api/v1/registration/coordinator/<session_id>/reject/
    Requires auth. Coordinator for the session's major can reject; session is deleted.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        person = _get_coordinator_person(request)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            session = RegistrationSession.objects.get(pk=session_id)
        except RegistrationSession.DoesNotExist:
            return Response(
                {"detail": "Session not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not can_coordinator_verify_session(person, session):
            return Response(
                {"detail": "Not allowed to verify this session"},
                status=status.HTTP_403_FORBIDDEN,
            )
        session.delete()
        resp = CoordinatorRejectResponseSerializer(
            {"message": "Registration rejected and removed"}
        )
        return Response(resp.data)
