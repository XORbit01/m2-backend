from rest_framework import serializers


class ProfileSettingsResponseSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    avatar_url = serializers.CharField(allow_null=True)

