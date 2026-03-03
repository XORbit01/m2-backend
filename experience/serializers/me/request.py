from rest_framework import serializers

from core.enums import ExperienceStatus, ExperienceType


class MyExperienceCreateRequestSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=[c[0] for c in ExperienceType.choices])
    status = serializers.ChoiceField(
        choices=[c[0] for c in ExperienceStatus.choices],
        required=False,
    )
    institution_id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    idea = serializers.CharField(required=False, allow_blank=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    lab_name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    supervisor_name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    supervisor_id = serializers.IntegerField(required=False, allow_null=True)
    keywords = serializers.CharField(required=False, allow_blank=True)
    links = serializers.JSONField(required=False)

