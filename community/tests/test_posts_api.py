"""Tests for community posts and comments API."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Person
from programs.models import Major, Program
from community.models import Post, PostComment

User = get_user_model()


def _create_user_with_person(email, full_name="Test", password="testpass123"):
    user = User.objects.create_user(username=email, email=email, password=password)
    person = Person.objects.create(full_name=full_name, email=email, user=user)
    return user, person


class CommunityPostsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_url = "/api/v1/community/posts/"

        self.user, self.person = _create_user_with_person("user@example.com", "Alice")
        self.major = Major.objects.create(code="M2DS", name="M2 Data Science")
        self.program = Program.objects.create(
            name="M2 DS",
            university="LU",
            degree_level="M2",
            major=self.major,
        )

    def test_get_posts_unauthenticated_returns_403(self):
        response = self.client.get(self.list_url)
        self.assertIn(response.status_code, (401, 403))

    def test_create_post_and_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.list_url,
            {
                "title": "Question about internship",
                "body": "How to find a supervisor?",
                "audiences": [
                    {"role": "SUPERVISORS", "major_id": self.major.id},
                    {"role": "STUDENTS", "major_id": None},
                ],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("id", data)
        post_id = data["id"]
        self.assertTrue(Post.objects.filter(id=post_id).exists())

        # List posts
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["posts"]), 1)
        post_item = data["posts"][0]
        self.assertEqual(post_item["title"], "Question about internship")
        self.assertEqual(post_item["comments_count"], 0)
        self.assertEqual(len(post_item["audiences"]), 2)


class CommunityCommentsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user, self.person = _create_user_with_person("user@example.com", "Alice")
        self.other_user, self.other_person = _create_user_with_person(
            "other@example.com", "Bob"
        )
        self.post = Post.objects.create(
            author=self.person,
            title="Welcome",
            body="First post",
        )

    def _comments_list_url(self, post_id):
        return f"/api/v1/community/posts/{post_id}/comments/"

    def _comments_create_url(self, post_id):
        return f"/api/v1/community/posts/{post_id}/comments/create/"

    def test_list_comments_unauthenticated_returns_403(self):
        response = self.client.get(self._comments_list_url(self.post.id))
        self.assertIn(response.status_code, (401, 403))

    def test_create_and_list_comments(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(
            self._comments_create_url(self.post.id),
            {"body": "Nice post"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(PostComment.objects.filter(post=self.post).count(), 1)

        response = self.client.get(self._comments_list_url(self.post.id))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["comments"]), 1)
        self.assertEqual(data["comments"][0]["body"], "Nice post")

