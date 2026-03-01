from rest_framework import serializers


class RegistrationSubmitResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()
