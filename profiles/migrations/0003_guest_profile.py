from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0002_merge_supervisor_into_teacher"),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="GuestProfile",
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
                    "note",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                (
                    "person",
                    models.OneToOneField(
                        on_delete=models.deletion.CASCADE,
                        related_name="guest_profile",
                        to="core.person",
                    ),
                ),
            ],
            options={
                "db_table": "profiles_guest_profile",
            },
        ),
    ]

