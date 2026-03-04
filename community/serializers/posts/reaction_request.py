from rest_framework import serializers

from core.enums import PostReactionType


class CommunityPostReactionRequestSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=[c[0] for c in PostReactionType.choices])

