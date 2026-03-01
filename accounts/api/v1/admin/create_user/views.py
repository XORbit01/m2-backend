from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Person

from accounts.serializers.admin.create_user.request import CreateUserRequestSerializer
from accounts.serializers.admin.create_user.response import CreateUserResponseSerializer

User = get_user_model()


class CreateUserView(APIView):
    """
    POST /api/v1/admin/users/
    Admin only. Creates User + Person with email and temporary password.
    """

    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = CreateUserRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        email = data["email"]
        password = data["password"]
        full_name = data["full_name"]

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

        resp = CreateUserResponseSerializer(
            {
                "user_id": user.id,
                "person_id": person.id,
                "email": user.email,
                "full_name": person.full_name,
            }
        )
        return Response(resp.data, status=status.HTTP_201_CREATED)
