from django.db import models

from core.enums import PostAudienceRole
from core.models import Person
from programs.models import Major


class Post(models.Model):
    author = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "community_post"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.title} by {self.author}"


class PostAudience(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="audiences",
    )
    role = models.CharField(
        max_length=32,
        choices=PostAudienceRole.choices,
    )
    major = models.ForeignKey(
        Major,
        on_delete=models.CASCADE,
        related_name="post_audiences",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "community_post_audience"

    def __str__(self):
        if self.major_id:
            return f"{self.role} for {self.major.code}"
        return self.role


class PostComment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="post_comments",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "community_post_comment"
        ordering = ("created_at",)

    def __str__(self):
        return f"Comment by {self.author} on {self.post_id}"

