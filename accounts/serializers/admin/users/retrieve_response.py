from rest_framework import serializers


class AdminUserRetrieveResponseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    person_id = serializers.IntegerField(allow_null=True)
    email = serializers.EmailField()
    full_name = serializers.CharField()
    roles = serializers.ListField(child=serializers.CharField())
    is_staff = serializers.BooleanField()
    is_active = serializers.BooleanField()
    is_superuser = serializers.BooleanField()
    created_at = serializers.DateTimeField(allow_null=True)
    updated_at = serializers.DateTimeField(allow_null=True)
