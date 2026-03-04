from rest_framework import serializers

from core.enums import PostReactionType


class CommunityPostReactionResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    post_id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=[c[0] for c in PostReactionType.choices])
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

