from rest_framework import serializers


class CoordinatorRejectResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
