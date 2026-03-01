from django.db import models

from core.enums import InstitutionType


class Institution(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=128)
    type = models.CharField(
        max_length=32,
        choices=InstitutionType.choices,
    )
    website = models.URLField(blank=True, default="")

    class Meta:
        db_table = "institutions_institution"

    def __str__(self):
        return self.name
