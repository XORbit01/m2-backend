from rest_framework import serializers


class CoordinatorAssignTeacherRequestSerializer(serializers.Serializer):
    teacher_id = serializers.IntegerField()
