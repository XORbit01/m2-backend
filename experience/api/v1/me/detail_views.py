from core.models import Person
from drf_spectacular.utils import extend_schema, extend_schema_view
from experience.models import Experience
from experience.serializers.me.create_response import (
    MyExperienceCreateResponseSerializer,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@extend_schema(responses={200: MyExperienceCreateResponseSerializer})
@extend_schema_view(
    put=extend_schema(responses={200: MyExperienceCreateResponseSerializer}),
    delete=extend_schema(responses={204: None}),
)
class MyExperienceDetailView(APIView):
    """
    PUT /api/v1/experience/me/<experience_id>/
    Update an experience that belongs to the authenticated person.

    DELETE /api/v1/experience/me/<experience_id>/
    Delete an experience that belongs to the authenticated person.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MyExperienceCreateResponseSerializer

    def _get_person(self, request):
        try:
            return request.user.person
        except Person.DoesNotExist:
            return None

    def _get_experience(self, person, experience_id):
        try:
            return Experience.objects.select_related("institution").get(
                pk=experience_id,
                person=person,
            )
        except Experience.DoesNotExist:
            return None

    def put(self, request, experience_id):
        person = self._get_person(request)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )

        experience = self._get_experience(person, experience_id)
        if experience is None:
            return Response(
                {"detail": "Experience not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # For now, allow client to change only status and idea/keywords/links via this endpoint,
        # to keep updates simple. Title/institution/type edits can be added later if needed.
        status_value = request.data.get("status")
        if status_value:
            experience.status = status_value
        if "idea" in request.data:
            experience.idea = request.data.get("idea") or ""
        if "keywords" in request.data:
            experience.keywords = request.data.get("keywords") or ""
        if "links" in request.data:
            experience.links = request.data.get("links") or {}

        experience.save()

        resp = MyExperienceCreateResponseSerializer(
            {
                "id": experience.id,
                "type": experience.type,
                "status": experience.status,
                "institution_id": experience.institution_id,
                "institution_name": experience.institution.name,
                "title": experience.title,
                "idea": experience.idea,
                "start_date": experience.start_date,
                "end_date": experience.end_date,
                "lab_name": experience.lab_name,
                "supervisor_name": experience.supervisor_name,
                "supervisor_id": experience.supervisor_id,
                "keywords": experience.keywords,
                "links": experience.links,
            }
        )
        return Response(resp.data)

    def delete(self, request, experience_id):
        person = self._get_person(request)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )

        experience = self._get_experience(person, experience_id)
        if experience is None:
            return Response(
                {"detail": "Experience not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        experience.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

