from rest_framework import serializers


class GuestRegisterRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    full_name = serializers.CharField(max_length=255)
    note = serializers.CharField(max_length=255, required=False, default="", allow_blank=True)
