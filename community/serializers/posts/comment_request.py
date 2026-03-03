from rest_framework import serializers


class CommunityCreateCommentRequestSerializer(serializers.Serializer):
    body = serializers.CharField()

