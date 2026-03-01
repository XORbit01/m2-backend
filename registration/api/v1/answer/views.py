import logging

from core.models import Person
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from registration.enums import RegistrationStep
from registration.helpers.state_machine import get_base_role_from_q1, get_next_step
from registration.models import RegistrationSession
from registration.serializers.answer.request import RegistrationAnswerRequestSerializer
from registration.serializers.answer.response import RegistrationAnswerResponseSerializer

log = logging.getLogger(__name__)


class RegistrationAnswerView(APIView):
    """
    POST /api/v1/registration/answer/
    Requires auth. Submit answer for current step; advances state and persists payload.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            person = request.user.person
        except Person.DoesNotExist:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )
        req_serializer = RegistrationAnswerRequestSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)
        data = req_serializer.validated_data

        session, _ = RegistrationSession.objects.get_or_create(
            person=person,
            defaults={"payload": {}},
        )
        if session.status != "PENDING":
            return Response(
                {"detail": "Registration already submitted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Build answer dict for state machine
        answer = {
            "finished_master": data.get("finished_master"),
            "has_internship": data.get("has_internship"),
            "had_internship": data.get("had_internship"),
            "is_phd_student": data.get("is_phd_student"),
            "is_working": data.get("is_working"),
        }
        next_step = get_next_step(
            session.current_step, answer, base_role=session.base_role
        )
        if next_step is None:
            return Response(
                {"detail": "Invalid transition or missing answer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Merge collection payloads into session.payload
        payload = dict(session.payload)
        if data.get("student_data") is not None:
            payload["student"] = data["student_data"]
        if data.get("alumni_data") is not None:
            payload["alumni"] = data["alumni_data"]
        if data.get("internship_data") is not None:
            payload.setdefault("internships", []).append(data["internship_data"])
        if data.get("phd_data") is not None:
            payload.setdefault("phd", []).append(data["phd_data"])
        if data.get("work_data") is not None:
            payload.setdefault("work", []).append(data["work_data"])

        if session.current_step == RegistrationStep.Q1_MASTER_STATUS.value:
            base_role = get_base_role_from_q1(answer)
            if base_role:
                session.base_role = base_role.value

        session.payload = payload
        session.current_step = next_step.value
        session.save(update_fields=["current_step", "payload", "base_role", "updated_at"])

        resp_serializer = RegistrationAnswerResponseSerializer(
            {
                "current_step": session.current_step,
                "payload": session.payload,
                "base_role": session.base_role,
                "status": session.status,
            }
        )
        return Response(resp_serializer.data)
