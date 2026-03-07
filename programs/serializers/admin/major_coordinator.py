from rest_framework import serializers


class AdminMajorCoordinatorAssignRequestSerializer(serializers.Serializer):
    coordinator_person_id = serializers.IntegerField()
    is_primary = serializers.BooleanField(required=False, default=False)
