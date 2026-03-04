import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Person
from registration.enums import RegistrationStep
from registration.helpers.state_machine import (get_base_role_from_q1,
                                                get_next_step,
                                                get_required_answer_key)
from registration.helpers.validators import validate_registration_answer
from registration.models import RegistrationSession
from registration.serializers.answer.request import \
    RegistrationAnswerRequestSerializer
from registration.serializers.answer.response import \
    RegistrationAnswerResponseSerializer
from registration.step_definitions import get_question_definition

log = logging.getLogger(__name__)


@extend_schema(
    request=RegistrationAnswerRequestSerializer,
    responses={200: RegistrationAnswerResponseSerializer},
)
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

        # Require the key(s) for the current step so we don't advance with wrong payload
        required_key = get_required_answer_key(session.current_step)
        if required_key is not None:
            if isinstance(required_key, tuple):
                if not any(data.get(k) is not None for k in required_key):
                    return Response(
                        {
                            "detail": "Missing required answer for this step",
                            "required_key": required_key[0],
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                # For yes/no steps that can have nested data, require nested data when True
                if session.current_step == RegistrationStep.Q2_INTERNSHIP.value:
                    if data.get("has_internship") is True and data.get("internship_data") is None:
                        return Response(
                            {"detail": "internship_data required when has_internship is true"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                if session.current_step == RegistrationStep.Q2_INTERNSHIP_ALUMNI.value:
                    if data.get("had_internship") is True and data.get("internship_data") is None:
                        return Response(
                            {"detail": "internship_data required when had_internship is true"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                if session.current_step == RegistrationStep.Q3_PHD.value:
                    if data.get("is_phd_student") is True and data.get("phd_data") is None:
                        return Response(
                            {"detail": "phd_data required when is_phd_student is true"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                if session.current_step == RegistrationStep.Q4_WORK.value:
                    if data.get("is_working") is True and data.get("work_data") is None:
                        return Response(
                            {"detail": "work_data required when is_working is true"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
            else:
                if data.get(required_key) is None:
                    return Response(
                        {
                            "detail": "Missing required answer for this step",
                            "required_key": required_key,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        # Validate IDs and institution name against DB
        validation_errors = validate_registration_answer(session.current_step, data)
        if validation_errors:
            return Response(
                {"detail": "Validation failed", "errors": validation_errors},
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

        question_def = get_question_definition(session.current_step)
        resp_serializer = RegistrationAnswerResponseSerializer(
            {
                "current_step": session.current_step,
                "payload": session.payload,
                "base_role": session.base_role,
                "status": session.status,
                "question": question_def,
            }
        )
        return Response(resp_serializer.data)
