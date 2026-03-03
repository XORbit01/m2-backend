from rest_framework import serializers


class TeacherSupervisionActionResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

