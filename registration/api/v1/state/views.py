import copy

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Person
from registration.enums import RegistrationStep
from registration.helpers.registration_options import enrich_question_with_options
from registration.models import RegistrationSession
from registration.serializers.state.response import \
    RegistrationStateResponseSerializer
from registration.step_definitions import get_question_definition


@extend_schema(responses={200: RegistrationStateResponseSerializer})
class RegistrationStateView(APIView):
    """
    GET /api/v1/registration/state/
    Requires auth. Returns current registration step and payload for the logged-in user's person.
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
        session, _ = RegistrationSession.objects.get_or_create(
            person=person,
            defaults={"payload": {}},
        )
        label = dict(RegistrationStep.choices).get(
            session.current_step, session.current_step
        )
        question_def = get_question_definition(session.current_step)
        if question_def:
            question_def = enrich_question_with_options(copy.deepcopy(question_def))
        next_key = (
            question_def.get("question_key") if question_def else _next_question_key(session.current_step)
        )
        data = {
            "current_step": session.current_step,
            "current_step_label": label,
            "payload": session.payload,
            "base_role": session.base_role,
            "status": session.status,
            "next_question_key": next_key,
            "question": question_def,
        }
        serializer = RegistrationStateResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


def _next_question_key(step: str) -> str | None:
    """Hardcoded question key for frontend."""
    keys = {
        "Q1_MASTER_STATUS": "finished_master",
        "Q2_INTERNSHIP": "has_internship",
        "Q2_INTERNSHIP_ALUMNI": "had_internship",
        "Q3_PHD": "is_phd_student",
        "Q4_WORK": "is_working",
    }
    return keys.get(step)
