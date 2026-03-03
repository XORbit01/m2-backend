from django.urls import path

from community.views import (
    CommunityPostCommentsCreateView,
    CommunityPostCommentsListView,
    CommunityPostDetailView,
    CommunityPostListCreateView,
)

app_name = "community"

urlpatterns = [
    path(
        "posts/",
        CommunityPostListCreateView.as_view(),
        name="community-posts",
    ),
    path(
        "posts/<int:post_id>/",
        CommunityPostDetailView.as_view(),
        name="community-post-detail",
    ),
    path(
        "posts/<int:post_id>/comments/",
        CommunityPostCommentsListView.as_view(),
        name="community-post-comments",
    ),
    path(
        "posts/<int:post_id>/comments/create/",
        CommunityPostCommentsCreateView.as_view(),
        name="community-post-comments-create",
    ),
]

