from core.models import Person
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers.profile_settings.request import (
    ProfileSettingsRequestSerializer,
)
from accounts.serializers.profile_settings.response import (
    ProfileSettingsResponseSerializer,
)


class ProfileSettingsView(APIView):
    """
    GET /api/v1/auth/profile/
    Returns basic profile settings for the authenticated user.

    PUT /api/v1/auth/profile/
    Updates basic profile settings (first_name, last_name, avatar) for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def _get_person(self, request):
        try:
            return request.user.person
        except Person.DoesNotExist:
            return None

    def get(self, request):
        person = self._get_person(request)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )

        avatar_url = person.avatar.url if person.avatar else None
        first_name = ""
        last_name = ""
        if person.full_name:
            parts = person.full_name.split(" ", 1)
            first_name = parts[0]
            if len(parts) == 2:
                last_name = parts[1]
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": person.email,
            "avatar_url": avatar_url,
        }
        serializer = ProfileSettingsResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    def put(self, request):
        person = self._get_person(request)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProfileSettingsRequestSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        # Derive existing first/last from current full_name
        existing_first = ""
        existing_last = ""
        if person.full_name:
            parts = person.full_name.split(" ", 1)
            existing_first = parts[0]
            if len(parts) == 2:
                existing_last = parts[1]

        new_first = validated.get("first_name", existing_first)
        new_last = validated.get("last_name", existing_last)
        person.full_name = " ".join(p for p in [new_first, new_last] if p)

        avatar = validated.get("avatar")
        if avatar is not None:
            person.avatar = avatar

        person.save()

        avatar_url = person.avatar.url if person.avatar else None
        resp = ProfileSettingsResponseSerializer(
            {
                "first_name": new_first,
                "last_name": new_last,
                "email": person.email,
                "avatar_url": avatar_url,
            }
        )
        return Response(resp.data)

