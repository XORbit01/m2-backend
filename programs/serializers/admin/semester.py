from rest_framework import serializers


class AdminSemesterItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    cohort_id = serializers.IntegerField()
    cohort_academic_year = serializers.CharField()
    program_name = serializers.CharField()
    name = serializers.CharField()


class AdminSemesterListResponseSerializer(serializers.Serializer):
    semesters = serializers.ListField(child=AdminSemesterItemSerializer())


class AdminSemesterRequestSerializer(serializers.Serializer):
    cohort_id = serializers.IntegerField()
    name = serializers.CharField(max_length=64)
