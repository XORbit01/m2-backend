from rest_framework import serializers


class AdminUserUpdateRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    full_name = serializers.CharField(max_length=255, required=False)
    password = serializers.CharField(min_length=8, write_only=True, required=False)
    is_active = serializers.BooleanField(required=False)
