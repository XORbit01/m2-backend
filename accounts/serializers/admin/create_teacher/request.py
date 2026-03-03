from rest_framework import serializers


class CreateTeacherRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    full_name = serializers.CharField(max_length=255)
    title = serializers.CharField(max_length=128)
    department = serializers.CharField(max_length=255)
    is_supervisor = serializers.BooleanField(default=False)
