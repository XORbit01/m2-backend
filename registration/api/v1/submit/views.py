import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Person
from registration.enums import RegistrationStatus, RegistrationStep
from registration.models import RegistrationSession
from registration.serializers.submit.request import \
    RegistrationSubmitRequestSerializer
from registration.serializers.submit.response import \
    RegistrationSubmitResponseSerializer

log = logging.getLogger(__name__)


@extend_schema(
    request=RegistrationSubmitRequestSerializer,
    responses={200: RegistrationSubmitResponseSerializer},
)
class RegistrationSubmitView(APIView):
    """
    POST /api/v1/registration/submit/
    Requires auth. Final submit when current_step is SUBMIT. Sets status to SUBMITTED.
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
        RegistrationSubmitRequestSerializer(data=request.data).is_valid(raise_exception=True)

        try:
            session = RegistrationSession.objects.get(person=person)
        except RegistrationSession.DoesNotExist:
            return Response(
                {"detail": "No registration session found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if session.current_step != RegistrationStep.SUBMIT.value:
            return Response(
                {"detail": "Registration not at submit step"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if session.status == RegistrationStatus.SUBMITTED.value:
            return Response(
                {"detail": "Already submitted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session.status = RegistrationStatus.SUBMITTED.value
        session.save(update_fields=["status", "updated_at"])

        resp = RegistrationSubmitResponseSerializer(
            {"status": session.status, "message": "Registration submitted successfully"}
        )
        return Response(resp.data)
