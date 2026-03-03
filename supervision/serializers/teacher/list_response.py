from rest_framework import serializers


class TeacherSupervisionItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    student_email = serializers.EmailField()
    status = serializers.CharField()


class TeacherSupervisionListResponseSerializer(serializers.Serializer):
    requests = serializers.ListField(
        child=TeacherSupervisionItemSerializer(),
    )

