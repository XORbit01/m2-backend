from core.enums import ExperienceStatus
from core.models import Person
from drf_spectacular.utils import extend_schema, extend_schema_view
from experience.models import Experience
from experience.serializers.me.create_response import (
    MyExperienceCreateResponseSerializer,
)
from experience.serializers.me.request import MyExperienceCreateRequestSerializer
from experience.serializers.me.response import MyExperiencesListResponseSerializer
from institutions.models import Institution
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@extend_schema_view(
    get=extend_schema(responses={200: MyExperiencesListResponseSerializer}),
    post=extend_schema(
        request=MyExperienceCreateRequestSerializer,
        responses={201: MyExperienceCreateResponseSerializer},
    ),
)
class MyExperiencesListCreateView(APIView):
    """
    GET /api/v1/experience/me/
    List all experience records (internships, PhD, work, other) for the authenticated person.

    POST /api/v1/experience/me/
    Create a new experience record for the authenticated person.
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

        experiences = (
            Experience.objects.filter(person=person)
            .select_related("institution", "supervisor")
            .order_by("-start_date", "-id")
        )
        items = [
            {
                "id": e.id,
                "type": e.type,
                "status": e.status,
                "institution_id": e.institution_id,
                "institution_name": e.institution.name,
                "title": e.title,
                "idea": e.idea,
                "start_date": e.start_date,
                "end_date": e.end_date,
                "lab_name": e.lab_name,
                "supervisor_name": e.supervisor_name,
                "supervisor_id": e.supervisor_id,
                "keywords": e.keywords,
                "links": e.links,
            }
            for e in experiences
        ]
        data = {"experiences": items}
        serializer = MyExperiencesListResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    def post(self, request):
        person = self._get_person(request)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )

        req = MyExperienceCreateRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        validated = req.validated_data

        try:
            institution = Institution.objects.get(pk=validated["institution_id"])
        except Institution.DoesNotExist:
            return Response(
                {"detail": "Institution not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        supervisor = None
        supervisor_id = validated.get("supervisor_id")
        if supervisor_id:
            try:
                supervisor = Person.objects.get(pk=supervisor_id)
            except Person.DoesNotExist:
                return Response(
                    {"detail": "Supervisor (person) not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        status_value = validated.get("status") or ExperienceStatus.ONGOING.value

        experience = Experience.objects.create(
            person=person,
            type=validated["type"],
            status=status_value,
            institution=institution,
            title=validated["title"],
            idea=validated.get("idea") or "",
            start_date=validated.get("start_date"),
            end_date=validated.get("end_date"),
            lab_name=validated.get("lab_name") or "",
            supervisor_name=validated.get("supervisor_name") or "",
            supervisor=supervisor,
            keywords=validated.get("keywords") or "",
            links=validated.get("links") or {},
        )

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
        return Response(resp.data, status=status.HTTP_201_CREATED)

