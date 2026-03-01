from rest_framework import serializers


class RegistrationAnswerResponseSerializer(serializers.Serializer):
    current_step = serializers.CharField()
    payload = serializers.JSONField()
    base_role = serializers.CharField(allow_null=True)
    status = serializers.CharField()
