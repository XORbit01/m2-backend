"""
Central registry for community (posts) views.
"""

from community.api.v1.posts.views import (
    CommunityPostCommentsListView,
    CommunityPostCommentsCreateView,
    CommunityPostDetailView,
    CommunityPostListCreateView,
)

__all__ = [
    "CommunityPostCommentsCreateView",
    "CommunityPostCommentsListView",
    "CommunityPostDetailView",
    "CommunityPostListCreateView",
]

