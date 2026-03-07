from rest_framework import serializers


class GuestRegisterResponseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    person_id = serializers.IntegerField()
    email = serializers.EmailField()
    full_name = serializers.CharField()
