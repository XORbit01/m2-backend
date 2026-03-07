from rest_framework import serializers

from core.enums import InstitutionType


class AdminInstitutionItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    country = serializers.CharField()
    type = serializers.CharField()
    website = serializers.URLField(allow_blank=True)


class AdminInstitutionListResponseSerializer(serializers.Serializer):
    institutions = serializers.ListField(child=AdminInstitutionItemSerializer())


class AdminInstitutionRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    country = serializers.CharField(max_length=128)
    type = serializers.ChoiceField(choices=[c[0] for c in InstitutionType.choices])
    website = serializers.URLField(required=False, allow_blank=True, default="")
