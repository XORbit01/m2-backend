from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.helpers.me import get_me_roles
from accounts.serializers.login.request import LoginRequestSerializer
from accounts.serializers.login.response import LoginResponseSerializer

User = get_user_model()


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


@extend_schema(
    request=LoginRequestSerializer,
    responses={200: LoginResponseSerializer},
)
class LoginView(APIView):
    """
    POST /api/v1/auth/login/
    Email + password. On success: session login + registration status.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        reg_complete, current_step, person_id = _get_registration_status(user)
        from core.models import Person

        try:
            person = user.person
        except Person.DoesNotExist:
            person = None
        roles = get_me_roles(person, user=user)
        data = {
            "user_id": user.id,
            "email": user.email,
            "registration_complete": reg_complete,
            "current_step": current_step,
            "person_id": person_id,
            "roles": roles,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }
        resp = LoginResponseSerializer(data=data)
        resp.is_valid(raise_exception=True)
        return Response(resp.data)
