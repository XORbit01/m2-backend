from rest_framework import serializers


class CourseOfferingItemSerializer(serializers.Serializer):
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


class CoordinatorOfferingsListResponseSerializer(serializers.Serializer):
    offerings = serializers.ListField(child=CourseOfferingItemSerializer())
