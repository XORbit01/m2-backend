from rest_framework import serializers


class ProfileSettingsRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255, required=False)
    last_name = serializers.CharField(max_length=255, required=False)
    avatar = serializers.FileField(required=False)

