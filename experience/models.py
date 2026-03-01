from django.db import models

from core.enums import ExperienceStatus, ExperienceType
from core.models import Person
from institutions.models import Institution


class Experience(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="experiences")
    type = models.CharField(
        max_length=32,
        choices=ExperienceType.choices,
    )
    status = models.CharField(
        max_length=32,
        choices=ExperienceStatus.choices,
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="hosted_experiences",
    )
    title = models.CharField(max_length=255)
    idea = models.TextField(blank=True, default="")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    lab_name = models.CharField(max_length=255, blank=True, default="")
    supervisor_name = models.CharField(max_length=255, blank=True, default="")
    supervisor = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervised_experiences",
    )
    keywords = models.TextField(blank=True, default="")
    links = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "experience_experience"

    def __str__(self):
        return f"{self.person} - {self.get_type_display()} at {self.institution}"
