from rest_framework import serializers


class CommunityCreateCommentResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    body = serializers.CharField()
    author_id = serializers.IntegerField()
    author_full_name = serializers.CharField()
    created_at = serializers.DateTimeField()


class CommunityCommentItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    body = serializers.CharField()
    author_id = serializers.IntegerField()
    author_full_name = serializers.CharField()
    created_at = serializers.DateTimeField()


class CommunityCommentsListResponseSerializer(serializers.Serializer):
    comments = serializers.ListField(
        child=CommunityCommentItemSerializer(),
    )

