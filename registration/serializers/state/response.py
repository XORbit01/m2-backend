from rest_framework import serializers


class RegistrationStateResponseSerializer(serializers.Serializer):
    current_step = serializers.CharField()
    current_step_label = serializers.CharField(required=False)
    payload = serializers.JSONField()
    base_role = serializers.CharField(allow_null=True)
    status = serializers.CharField()
    next_question_key = serializers.CharField(allow_null=True, required=False)
