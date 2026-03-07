from rest_framework import serializers


class AdminProgramItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    university = serializers.CharField()
    degree_level = serializers.CharField()
    major_id = serializers.IntegerField(allow_null=True)
    major_code = serializers.CharField(allow_null=True)


class AdminProgramListResponseSerializer(serializers.Serializer):
    programs = serializers.ListField(child=AdminProgramItemSerializer())


class AdminProgramRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    university = serializers.CharField(max_length=255)
    degree_level = serializers.CharField(max_length=64)
    major_id = serializers.IntegerField(required=False, allow_null=True)
