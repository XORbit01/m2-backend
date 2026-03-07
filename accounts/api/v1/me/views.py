from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.helpers.me import build_me_profile, get_me_roles
from accounts.serializers.me.response import MeResponseSerializer


def _get_registration_status(user):
    """Return registration_complete, current_step, person_id."""
    from core.models import Person
    from registration.models import RegistrationSession

    try:
        person = user.person
    except Person.DoesNotExist:
        return False, None, None
    try:
        session = person.registration_session
    except RegistrationSession.DoesNotExist:
        return False, "Q1_MASTER_STATUS", person.id
    if session.status == "ACCEPTED":
        return True, None, person.id
    return False, session.current_step, person.id


@extend_schema(responses={200: MeResponseSerializer})
class MeView(APIView):
    """
    GET /api/v1/auth/me/
    Requires auth. Returns current user, registration status, roles, and
    role-based profile (student, teacher, coordinator).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        reg_complete, current_step, person_id = _get_registration_status(user)

        person = None
        try:
            from core.models import Person

            person = user.person
        except Person.DoesNotExist:
            pass

        roles = get_me_roles(person, user=user)
        profile = build_me_profile(person)

        data = {
            "user_id": user.id,
            "email": user.email,
            "registration_complete": reg_complete,
            "current_step": current_step,
            "person_id": person_id,
            "roles": roles,
            "profile": profile,
        }
        serializer = MeResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
