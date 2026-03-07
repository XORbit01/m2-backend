from rest_framework import serializers


class AdminCourseItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    program_id = serializers.IntegerField()
    program_name = serializers.CharField()
    code = serializers.CharField()
    title = serializers.CharField()
    major_id = serializers.IntegerField(allow_null=True)
    major_code = serializers.CharField(allow_null=True)


class AdminCourseListResponseSerializer(serializers.Serializer):
    courses = serializers.ListField(child=AdminCourseItemSerializer())


class AdminCourseRequestSerializer(serializers.Serializer):
    program_id = serializers.IntegerField()
    code = serializers.CharField(max_length=64)
    title = serializers.CharField(max_length=255)
