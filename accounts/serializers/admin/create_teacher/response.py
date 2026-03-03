from rest_framework import serializers


class CreateTeacherResponseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    person_id = serializers.IntegerField()
    teacher_profile_id = serializers.IntegerField()
    email = serializers.EmailField()
    full_name = serializers.CharField()
    title = serializers.CharField()
    department = serializers.CharField()
    is_supervisor = serializers.BooleanField()
