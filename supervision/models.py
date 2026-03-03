from django.db import models

from core.enums import SupervisionStatus
from core.models import Person


class Supervision(models.Model):
    student = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="supervisions_as_student",
    )
    teacher = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="supervisions_as_teacher",
    )
    status = models.CharField(
        max_length=16,
        choices=SupervisionStatus.choices,
        default=SupervisionStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "supervision_supervision"

    def __str__(self):
        return f"{self.student} supervised by {self.teacher} ({self.status})"

