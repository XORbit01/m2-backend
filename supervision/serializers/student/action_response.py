from rest_framework import serializers


class StudentSupervisionActionResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

