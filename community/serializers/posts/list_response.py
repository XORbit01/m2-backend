from rest_framework import serializers


class CommunityPostAudienceItemSerializer(serializers.Serializer):
    role = serializers.CharField()
    major_id = serializers.IntegerField(allow_null=True)
    major_code = serializers.CharField(allow_null=True)
    major_name = serializers.CharField(allow_null=True)


class CommunityPostItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    body = serializers.CharField()
    author_id = serializers.IntegerField()
    author_full_name = serializers.CharField()
    created_at = serializers.DateTimeField()
    audiences = serializers.ListField(
        child=CommunityPostAudienceItemSerializer(),
    )
    comments_count = serializers.IntegerField()


class CommunityPostListResponseSerializer(serializers.Serializer):
    posts = serializers.ListField(
        child=CommunityPostItemSerializer(),
    )

