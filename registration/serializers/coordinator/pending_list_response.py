from rest_framework import serializers


class PendingSessionItemSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    person_id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    base_role = serializers.CharField(allow_null=True)
    payload = serializers.JSONField()
    created_at = serializers.DateTimeField()


class CoordinatorPendingListResponseSerializer(serializers.Serializer):
    sessions = serializers.ListField(child=PendingSessionItemSerializer())
