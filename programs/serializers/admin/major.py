from rest_framework import serializers


class AdminMajorItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()


class AdminMajorListResponseSerializer(serializers.Serializer):
    majors = serializers.ListField(child=AdminMajorItemSerializer())


class AdminMajorRequestSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=32)
    name = serializers.CharField(max_length=255)
