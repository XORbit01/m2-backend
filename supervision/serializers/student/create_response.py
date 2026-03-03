from rest_framework import serializers


class StudentCreateSupervisionResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    teacher_id = serializers.IntegerField()
    status = serializers.CharField()

