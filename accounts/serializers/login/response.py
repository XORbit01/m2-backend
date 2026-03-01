from rest_framework import serializers


class LoginResponseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    email = serializers.EmailField()
    registration_complete = serializers.BooleanField()
    current_step = serializers.CharField(allow_null=True)
    person_id = serializers.IntegerField(allow_null=True)
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
