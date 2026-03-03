from rest_framework import serializers


class StudentSupervisionItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    teacher_id = serializers.IntegerField()
    teacher_name = serializers.CharField()
    teacher_email = serializers.EmailField()
    status = serializers.CharField()


class StudentSupervisionListResponseSerializer(serializers.Serializer):
    supervisions = serializers.ListField(
        child=StudentSupervisionItemSerializer(),
    )

