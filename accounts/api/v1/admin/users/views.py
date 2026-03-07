"""
Admin user management: list, create, retrieve, update, delete.
"""

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.helpers.me import get_me_roles
from accounts.serializers.admin.users.list_response import (
    AdminUserListResponseSerializer,
)
from accounts.serializers.admin.users.retrieve_response import (
    AdminUserRetrieveResponseSerializer,
)
from accounts.serializers.admin.users.update_request import (
    AdminUserUpdateRequestSerializer,
)
from accounts.serializers.admin.users.update_response import (
    AdminUserUpdateResponseSerializer,
)
from accounts.serializers.admin.create_user.request import CreateUserRequestSerializer
from accounts.serializers.admin.create_user.response import CreateUserResponseSerializer
from core.models import Person

User = get_user_model()


def _build_user_item(user):
    """Build user dict for list/retrieve responses."""
    try:
        person = user.person
        person_id = person.id
        full_name = person.full_name
        updated_at = person.updated_at
    except Person.DoesNotExist:
        person_id = None
        full_name = getattr(user, "get_full_name", lambda: "")().strip() or user.email
        updated_at = None
    roles = get_me_roles(person if person_id else None, user=user)
    return {
        "user_id": user.id,
        "person_id": person_id,
        "email": user.email,
        "full_name": full_name,
        "roles": roles,
        "is_staff": user.is_staff,
        "is_active": user.is_active,
        "is_superuser": getattr(user, "is_superuser", False),
        "created_at": getattr(user, "date_joined", None),
        "updated_at": updated_at,
    }


@extend_schema_view(
    get=extend_schema(responses={200: AdminUserListResponseSerializer}),
    post=extend_schema(
        request=CreateUserRequestSerializer,
        responses={201: CreateUserResponseSerializer},
    ),
)
class AdminUserListCreateView(APIView):
    """
    GET /api/v1/auth/admin/users/
    Admin only. List all users with roles and basic info.

    POST /api/v1/auth/admin/users/
    Admin only. Create user (delegates to CreateUserView).
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all().order_by("-date_joined")
        items = [_build_user_item(u) for u in users]
        data = {"users": items}
        serializer = AdminUserListResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    def post(self, request):
        from accounts.api.v1.admin.create_user.views import CreateUserView

        return CreateUserView().post(request)


@extend_schema_view(
    get=extend_schema(responses={200: AdminUserRetrieveResponseSerializer}),
    put=extend_schema(
        request=AdminUserUpdateRequestSerializer,
        responses={200: AdminUserUpdateResponseSerializer},
    ),
    delete=extend_schema(responses={204: None}),
)
class AdminUserDetailView(APIView):
    """
    GET /api/v1/auth/admin/users/<user_id>/
    Admin only. Retrieve a single user with full details.

    PUT /api/v1/auth/admin/users/<user_id>/
    Admin only. Update user and person (email, full_name, password, is_active).

    DELETE /api/v1/auth/admin/users/<user_id>/
    Admin only. Delete user and related person.
    """

    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = _build_user_item(user)
        serializer = AdminUserRetrieveResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    def put(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AdminUserUpdateRequestSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user_update_fields = []
        if "email" in data:
            email = data["email"]
            if User.objects.filter(email=email).exclude(pk=user.id).exists():
                return Response(
                    {"detail": "User with this email already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Person.objects.filter(email=email).exclude(user=user).exists():
                return Response(
                    {"detail": "Person with this email already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.email = email
            user.username = email
            user_update_fields.extend(["email", "username"])
        if "password" in data and data["password"]:
            user.set_password(data["password"])
            user_update_fields.append("password")
        if "is_active" in data:
            user.is_active = data["is_active"]
            user_update_fields.append("is_active")
        if user_update_fields:
            user.save(update_fields=user_update_fields)

        try:
            person = user.person
        except Person.DoesNotExist:
            person = None
        if person:
            update_fields = []
            if "full_name" in data:
                person.full_name = data["full_name"]
                update_fields.append("full_name")
            if "email" in data:
                person.email = data["email"]
                update_fields.append("email")
            if update_fields:
                person.save(update_fields=update_fields)

        try:
            person = user.person
        except Person.DoesNotExist:
            person = None
        resp_data = {
            "user_id": user.id,
            "person_id": person.id if person else None,
            "email": user.email,
            "full_name": person.full_name if person else user.email,
            "is_active": user.is_active,
        }
        return Response(AdminUserUpdateResponseSerializer(resp_data).data)

    def delete(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            person = user.person
        except Person.DoesNotExist:
            person = None
        user.delete()
        if person:
            person.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
