import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("core", "0001_initial"),
        ("programs", "0002_add_program_major_optional_teacher"),
    ]

    operations = [
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("body", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="posts",
                        to="core.person",
                    ),
                ),
            ],
            options={
                "db_table": "community_post",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="PostComment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("body", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="post_comments",
                        to="core.person",
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="community.post",
                    ),
                ),
            ],
            options={
                "db_table": "community_post_comment",
                "ordering": ("created_at",),
            },
        ),
        migrations.CreateModel(
            name="PostAudience",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("GENERAL", "General"),
                            ("STUDENTS", "Students"),
                            ("SUPERVISORS", "Supervisors"),
                            ("TEACHERS", "Teachers"),
                            ("ALUMNI", "Alumni"),
                            ("GUESTS", "Guests"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "major",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="post_audiences",
                        to="programs.major",
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="audiences",
                        to="community.post",
                    ),
                ),
            ],
            options={
                "db_table": "community_post_audience",
            },
        ),
    ]

