from rest_framework import serializers


class TeacherItemSerializer(serializers.Serializer):
    person_id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    title = serializers.CharField()
    department = serializers.CharField()
    is_supervisor = serializers.BooleanField()


class CoordinatorTeachersListResponseSerializer(serializers.Serializer):
    teachers = serializers.ListField(child=TeacherItemSerializer())
