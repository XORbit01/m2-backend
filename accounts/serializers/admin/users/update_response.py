from rest_framework import serializers


class AdminUserUpdateResponseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    person_id = serializers.IntegerField(allow_null=True)
    email = serializers.EmailField()
    full_name = serializers.CharField()
    is_active = serializers.BooleanField()
