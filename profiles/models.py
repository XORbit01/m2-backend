from django.db import models

from core.enums import StudentStatus
from core.models import Person


class StudentProfile(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name="student_profile")
    student_number = models.CharField(max_length=64)
    current_status = models.CharField(
        max_length=32,
        choices=StudentStatus.choices,
        default=StudentStatus.ACTIVE,
    )

    class Meta:
        db_table = "profiles_student_profile"

    def __str__(self):
        return f"Student {self.person} ({self.student_number})"


class AlumniProfile(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name="alumni_profile")
    graduation_year = models.IntegerField()
    current_country = models.CharField(max_length=128)

    class Meta:
        db_table = "profiles_alumni_profile"

    def __str__(self):
        return f"Alumni {self.person} ({self.graduation_year})"


class TeacherProfile(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name="teacher_profile")
    title = models.CharField(max_length=128)
    department = models.CharField(max_length=255)
    is_supervisor = models.BooleanField(default=False)

    class Meta:
        db_table = "profiles_teacher_profile"

    def __str__(self):
        return f"{self.title} {self.person}"


class GuestProfile(models.Model):
    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        related_name="guest_profile",
    )
    note = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        db_table = "profiles_guest_profile"

    def __str__(self):
        return f"Guest {self.person}"
