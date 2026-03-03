from rest_framework import serializers


class CoordinatorAssignTeacherResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
