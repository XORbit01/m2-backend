from rest_framework import serializers


class RegistrationAnswerRequestSerializer(serializers.Serializer):
    """Payload for POST /registration/answer. Keys depend on current step."""

    finished_master = serializers.BooleanField(required=False)
    has_internship = serializers.BooleanField(required=False)
    had_internship = serializers.BooleanField(required=False)
    is_phd_student = serializers.BooleanField(required=False)
    is_working = serializers.BooleanField(required=False)
    # Data collection payloads (merged into session.payload)
    student_data = serializers.JSONField(required=False)
    alumni_data = serializers.JSONField(required=False)
    internship_data = serializers.JSONField(required=False)
    phd_data = serializers.JSONField(required=False)
    work_data = serializers.JSONField(required=False)
