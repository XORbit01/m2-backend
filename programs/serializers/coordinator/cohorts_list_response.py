from rest_framework import serializers


class CoordinatorCohortItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    academic_year = serializers.CharField()
    program_id = serializers.IntegerField()
    program_name = serializers.CharField()
    major_id = serializers.IntegerField(allow_null=True)
    major_code = serializers.CharField(allow_null=True)


class CoordinatorCohortsListResponseSerializer(serializers.Serializer):
    cohorts = serializers.ListField(child=CoordinatorCohortItemSerializer())
