from rest_framework import serializers

from core.enums import PostAudienceRole


class CommunityPostAudienceItemRequestSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=[c[0] for c in PostAudienceRole.choices])
    major_id = serializers.IntegerField(required=False, allow_null=True)


class CommunityCreatePostRequestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    body = serializers.CharField()
    audiences = serializers.ListField(
        child=CommunityPostAudienceItemRequestSerializer(),
        allow_empty=False,
    )

