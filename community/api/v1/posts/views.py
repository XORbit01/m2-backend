from programs.models import Major
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from community.helpers.participation import get_or_create_community_author_person
from community.models import Post, PostAudience, PostComment, PostReaction
from community.serializers.posts.comment_request import (
    CommunityCreateCommentRequestSerializer,
)
from community.serializers.posts.comment_response import (
    CommunityCommentsListResponseSerializer,
    CommunityCreateCommentResponseSerializer,
)
from community.serializers.posts.create_request import (
    CommunityCreatePostRequestSerializer,
)
from community.serializers.posts.create_response import (
    CommunityCreatePostResponseSerializer,
)
from community.serializers.posts.list_response import (
    CommunityPostListResponseSerializer,
)
from community.serializers.posts.reaction_request import (
    CommunityPostReactionRequestSerializer,
)
from community.serializers.posts.reaction_response import (
    CommunityPostReactionResponseSerializer,
)


class CommunityPostListCreateView(APIView):
    """
    GET /api/v1/community/posts/
    List all community posts with audiences, comment counts, and reactions.

    POST /api/v1/community/posts/
    Create a new community post with audiences.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            person = request.user.person
        except Exception:
            person = None

        posts = (
            Post.objects.all()
            .select_related("author")
            .prefetch_related("audiences", "comments", "reactions")
        )
        items = []
        for post in posts:
            audiences = []
            for a in post.audiences.all():
                major = a.major
                audiences.append(
                    {
                        "role": a.role,
                        "major_id": major.id if major else None,
                        "major_code": major.code if major else None,
                        "major_name": major.name if major else None,
                    }
                )

            totals = {
                "LIKE": 0,
                "INSIGHTFUL": 0,
                "INTERESTING": 0,
                "THANKS": 0,
                "SUPPORT": 0,
            }
            my_reaction = None
            for reaction in post.reactions.all():
                if reaction.type in totals:
                    totals[reaction.type] += 1
                if person is not None and reaction.person_id == person.id:
                    my_reaction = reaction.type

            items.append(
                {
                    "id": post.id,
                    "title": post.title,
                    "body": post.body,
                    "author_id": post.author_id,
                    "author_full_name": post.author.full_name,
                    "created_at": post.created_at,
                    "audiences": audiences,
                    "comments_count": post.comments.count(),
                    "reactions": {
                        "totals": totals,
                        "my_reaction": my_reaction,
                    },
                }
            )
        data = {"posts": items}
        serializer = CommunityPostListResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    def post(self, request):
        person = get_or_create_community_author_person(request.user)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )

        req = CommunityCreatePostRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        validated = req.validated_data

        post = Post.objects.create(
            author=person,
            title=validated["title"],
            body=validated["body"],
        )

        for audience in validated["audiences"]:
            major = None
            major_id = audience.get("major_id")
            if major_id is not None:
                try:
                    major = Major.objects.get(pk=major_id)
                except Major.DoesNotExist:
                    return Response(
                        {"detail": "Major not found"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            PostAudience.objects.create(
                post=post,
                role=audience["role"],
                major=major,
            )

        resp = CommunityCreatePostResponseSerializer(
            {
                "id": post.id,
                "title": post.title,
                "body": post.body,
            }
        )
        return Response(resp.data, status=status.HTTP_201_CREATED)


class CommunityPostDetailView(APIView):
    """
    GET /api/v1/community/posts/<post_id>/
    Retrieve a single post with audiences, comment count, and reactions.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        try:
            person = request.user.person
        except Exception:
            person = None

        try:
            post = (
                Post.objects.select_related("author")
                .prefetch_related("audiences__major", "comments", "reactions")
                .get(pk=post_id)
            )
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        audiences = []
        for a in post.audiences.select_related("major").all():
            major = a.major
            audiences.append(
                {
                    "role": a.role,
                    "major_id": major.id if major else None,
                    "major_code": major.code if major else None,
                    "major_name": major.name if major else None,
                }
            )

        totals = {
            "LIKE": 0,
            "INSIGHTFUL": 0,
            "INTERESTING": 0,
            "THANKS": 0,
            "SUPPORT": 0,
        }
        my_reaction = None
        for reaction in post.reactions.all():
            if reaction.type in totals:
                totals[reaction.type] += 1
            if person is not None and reaction.person_id == person.id:
                my_reaction = reaction.type

        data = {
            "posts": [
                {
                    "id": post.id,
                    "title": post.title,
                    "body": post.body,
                    "author_id": post.author_id,
                    "author_full_name": post.author.full_name,
                    "created_at": post.created_at,
                    "audiences": audiences,
                    "comments_count": post.comments.count(),
                    "reactions": {
                        "totals": totals,
                        "my_reaction": my_reaction,
                    },
                }
            ]
        }
        serializer = CommunityPostListResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class CommunityPostCommentsListView(APIView):
    """
    GET /api/v1/community/posts/<post_id>/comments/
    List comments for a post.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        comments = (
            PostComment.objects.filter(post=post)
            .select_related("author")
            .order_by("created_at")
        )
        items = [
            {
                "id": c.id,
                "body": c.body,
                "author_id": c.author_id,
                "author_full_name": c.author.full_name,
                "created_at": c.created_at,
            }
            for c in comments
        ]
        data = {"comments": items}
        serializer = CommunityCommentsListResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class CommunityPostCommentsCreateView(APIView):
    """
    POST /api/v1/community/posts/<post_id>/comments/
    Create a comment on a post.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        person = get_or_create_community_author_person(request.user)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        req = CommunityCreateCommentRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)

        comment = PostComment.objects.create(
            post=post,
            author=person,
            body=req.validated_data["body"],
        )

        resp = CommunityCreateCommentResponseSerializer(
            {
                "id": comment.id,
                "body": comment.body,
                "author_id": comment.author_id,
                "author_full_name": comment.author.full_name,
                "created_at": comment.created_at,
            }
        )
        return Response(resp.data, status=status.HTTP_201_CREATED)


class CommunityPostReactionsView(APIView):
    """
    POST /api/v1/community/posts/<post_id>/reactions/
    Set or update the current user's reaction on a post.

    DELETE /api/v1/community/posts/<post_id>/reactions/
    Remove the current user's reaction on a post (if any).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        person = get_or_create_community_author_person(request.user)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        req = CommunityPostReactionRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        reaction_type = req.validated_data["type"]

        reaction, _created = PostReaction.objects.update_or_create(
            post=post,
            person=person,
            defaults={"type": reaction_type},
        )

        resp = CommunityPostReactionResponseSerializer(
            {
                "id": reaction.id,
                "post_id": post.id,
                "type": reaction.type,
                "created_at": reaction.created_at,
                "updated_at": reaction.updated_at,
            }
        )
        return Response(resp.data, status=status.HTTP_200_OK)

    def delete(self, request, post_id):
        person = get_or_create_community_author_person(request.user)
        if person is None:
            return Response(
                {"detail": "User has no linked person"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        PostReaction.objects.filter(post=post, person=person).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

