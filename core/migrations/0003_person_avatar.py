from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_person_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="avatar",
            field=models.FileField(
                upload_to="avatars/",
                null=True,
                blank=True,
            ),
        ),
    ]

