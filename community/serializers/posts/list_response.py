from rest_framework import serializers

from core.enums import PostReactionType


class CommunityPostAudienceItemSerializer(serializers.Serializer):
    role = serializers.CharField()
    major_id = serializers.IntegerField(allow_null=True)
    major_code = serializers.CharField(allow_null=True)
    major_name = serializers.CharField(allow_null=True)


class CommunityPostReactionsTotalsSerializer(serializers.Serializer):
    LIKE = serializers.IntegerField()
    INSIGHTFUL = serializers.IntegerField()
    INTERESTING = serializers.IntegerField()
    THANKS = serializers.IntegerField()
    SUPPORT = serializers.IntegerField()


class CommunityPostReactionsSerializer(serializers.Serializer):
    totals = CommunityPostReactionsTotalsSerializer()
    my_reaction = serializers.ChoiceField(
        choices=[c[0] for c in PostReactionType.choices],
        allow_null=True,
    )


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
    reactions = CommunityPostReactionsSerializer()


class CommunityPostListResponseSerializer(serializers.Serializer):
    posts = serializers.ListField(
        child=CommunityPostItemSerializer(),
    )
