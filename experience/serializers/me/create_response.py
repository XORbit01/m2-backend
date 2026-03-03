from rest_framework import serializers


class MyExperienceCreateResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    status = serializers.CharField()
    institution_id = serializers.IntegerField()
    institution_name = serializers.CharField()
    title = serializers.CharField()
    idea = serializers.CharField()
    start_date = serializers.DateField(allow_null=True)
    end_date = serializers.DateField(allow_null=True)
    lab_name = serializers.CharField()
    supervisor_name = serializers.CharField()
    supervisor_id = serializers.IntegerField(allow_null=True)
    keywords = serializers.CharField()
    links = serializers.JSONField()

