from django.db import models

from core.enums import EnrollmentStatus
from core.models import Person
from programs.models import Cohort, Major


class Enrollment(models.Model):
    student = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="enrollments")
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name="memberships")
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(
        max_length=32,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.ACTIVE,
    )

    class Meta:
        db_table = "enrollment_enrollment"

    def __str__(self):
        return f"{self.student} in {self.cohort} ({self.major})"
