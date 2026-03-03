from rest_framework import serializers


class ExperienceItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    status = serializers.CharField()
    institution_id = serializers.IntegerField()
    institution_name = serializers.CharField()
    title = serializers.CharField()
    idea = serializers.CharField(allow_blank=True)
    start_date = serializers.DateField(allow_null=True)
    end_date = serializers.DateField(allow_null=True)
    lab_name = serializers.CharField(allow_blank=True)
    supervisor_name = serializers.CharField(allow_blank=True)
    supervisor_id = serializers.IntegerField(allow_null=True)
    keywords = serializers.CharField(allow_blank=True)
    links = serializers.JSONField()


class MyExperiencesListResponseSerializer(serializers.Serializer):
    experiences = serializers.ListField(
        child=ExperienceItemSerializer(),
    )

