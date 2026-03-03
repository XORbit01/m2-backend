from rest_framework import serializers


class StudentCreateSupervisionRequestSerializer(serializers.Serializer):
    teacher_id = serializers.IntegerField()

