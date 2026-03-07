from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers.register_guest.request import GuestRegisterRequestSerializer
from accounts.serializers.register_guest.response import GuestRegisterResponseSerializer
from core.models import Person
from profiles.models import GuestProfile

User = get_user_model()


@extend_schema(
    request=GuestRegisterRequestSerializer,
    responses={201: GuestRegisterResponseSerializer},
)
class GuestRegisterView(APIView):
    """
    POST /api/v1/auth/register/guest/
    Public. Creates User + Person + GuestProfile. Client should then call login.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GuestRegisterRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        email = data["email"]
        password = data["password"]
        full_name = data["full_name"]
        note = data.get("note") or ""

        if User.objects.filter(email=email).exists():
            return Response(
                {"detail": "User with this email already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Person.objects.filter(email=email).exists():
            return Response(
                {"detail": "Person with this email already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
        )
        person = Person.objects.create(
            full_name=full_name,
            email=email,
            user=user,
        )
        GuestProfile.objects.create(person=person, note=note[:255] if note else "")

        resp = GuestRegisterResponseSerializer(
            {
                "user_id": user.id,
                "person_id": person.id,
                "email": user.email,
                "full_name": person.full_name,
            }
        )
        return Response(resp.data, status=status.HTTP_201_CREATED)
