from rest_framework import serializers


class CoordinatorStudentItemSerializer(serializers.Serializer):
    person_id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    student_number = serializers.CharField(allow_blank=True)
    enrollment_id = serializers.IntegerField()
    cohort_id = serializers.IntegerField()
    cohort_academic_year = serializers.CharField()
    major_id = serializers.IntegerField()
    major_code = serializers.CharField()
    enrollment_status = serializers.CharField()


class CoordinatorStudentsListResponseSerializer(serializers.Serializer):
    students = serializers.ListField(child=CoordinatorStudentItemSerializer())
