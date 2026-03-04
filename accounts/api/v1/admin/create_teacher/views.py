from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers.admin.create_teacher.request import (
    CreateTeacherRequestSerializer,
)
from accounts.serializers.admin.create_teacher.response import (
    CreateTeacherResponseSerializer,
)
from core.models import Person
from profiles.models import TeacherProfile

User = get_user_model()


@extend_schema(
    request=CreateTeacherRequestSerializer,
    responses={201: CreateTeacherResponseSerializer},
)
class CreateTeacherView(APIView):
    """
    POST /api/v1/auth/admin/teachers/
    Admin only. Creates User + Person + TeacherProfile.
    """

    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = CreateTeacherRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        email = data["email"]
        password = data["password"]
        full_name = data["full_name"]
        title = data["title"]
        department = data["department"]
        is_supervisor = data["is_supervisor"]

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
        teacher_profile = TeacherProfile.objects.create(
            person=person,
            title=title,
            department=department,
            is_supervisor=is_supervisor,
        )

        resp = CreateTeacherResponseSerializer(
            {
                "user_id": user.id,
                "person_id": person.id,
                "teacher_profile_id": teacher_profile.id,
                "email": user.email,
                "full_name": person.full_name,
                "title": title,
                "department": department,
                "is_supervisor": is_supervisor,
            }
        )
        return Response(resp.data, status=status.HTTP_201_CREATED)
