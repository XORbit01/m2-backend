from rest_framework import serializers


class AdminOfferingItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    course_code = serializers.CharField()
    course_title = serializers.CharField()
    cohort_id = serializers.IntegerField()
    cohort_academic_year = serializers.CharField()
    semester_id = serializers.IntegerField()
    semester_name = serializers.CharField()
    teacher_id = serializers.IntegerField(allow_null=True)
    teacher_name = serializers.CharField(allow_null=True)


class AdminOfferingListResponseSerializer(serializers.Serializer):
    offerings = serializers.ListField(child=AdminOfferingItemSerializer())


class AdminOfferingRequestSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    cohort_id = serializers.IntegerField()
    semester_id = serializers.IntegerField()
    teacher_id = serializers.IntegerField(required=False, allow_null=True)
