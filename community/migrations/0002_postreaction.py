from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("community", "0001_initial"),
        ("core", "0003_person_avatar"),
    ]

    operations = [
        migrations.CreateModel(
            name="PostReaction",
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
                    "type",
                    models.CharField(
                        max_length=32,
                        choices=[
                            ("LIKE", "Like"),
                            ("INSIGHTFUL", "Insightful"),
                            ("INTERESTING", "Interesting"),
                            ("THANKS", "Thanks"),
                            ("SUPPORT", "Support"),
                        ],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="post_reactions",
                        to="core.person",
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reactions",
                        to="community.post",
                    ),
                ),
            ],
            options={
                "db_table": "community_post_reaction",
                "ordering": ("-created_at",),
            },
        ),
        migrations.AlterUniqueTogether(
            name="postreaction",
            unique_together={("post", "person")},
        ),
    ]

