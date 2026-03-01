from django.db import models

from core.models import Person


class Publication(models.Model):
    title = models.CharField(max_length=512)
    year = models.IntegerField()
    venue = models.CharField(max_length=255)
    doi_or_url = models.CharField(max_length=512, blank=True, default="")

    class Meta:
        db_table = "publications_publication"

    def __str__(self):
        return f"{self.title} ({self.year})"


class PublicationAuthor(models.Model):
    publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name="authorships",
    )
    author = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="authored_publications",
    )
    author_order = models.IntegerField()

    class Meta:
        db_table = "publications_publication_author"

    def __str__(self):
        return f"{self.publication} - {self.author} (#{self.author_order})"
