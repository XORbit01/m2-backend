from rest_framework import serializers


class CoordinatorAcceptResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()
