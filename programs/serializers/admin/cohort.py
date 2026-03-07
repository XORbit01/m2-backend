from rest_framework import serializers


class AdminCohortItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    program_id = serializers.IntegerField()
    program_name = serializers.CharField()
    academic_year = serializers.CharField()
    major_id = serializers.IntegerField(allow_null=True)
    major_code = serializers.CharField(allow_null=True)


class AdminCohortListResponseSerializer(serializers.Serializer):
    cohorts = serializers.ListField(child=AdminCohortItemSerializer())


class AdminCohortRequestSerializer(serializers.Serializer):
    program_id = serializers.IntegerField()
    academic_year = serializers.CharField(max_length=32)
