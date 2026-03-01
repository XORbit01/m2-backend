from django.db import models

from core.models import Person

from .enums import BaseRole, RegistrationStatus, RegistrationStep


class RegistrationSession(models.Model):
    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        related_name="registration_session",
    )
    current_step = models.CharField(
        max_length=64,
        choices=RegistrationStep.choices,
        default=RegistrationStep.Q1_MASTER_STATUS,
    )
    payload = models.JSONField(default=dict)
    base_role = models.CharField(
        max_length=32,
        choices=BaseRole.choices,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=32,
        choices=RegistrationStatus.choices,
        default=RegistrationStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "registration_registration_session"

    def __str__(self):
        return f"{self.person} - {self.current_step} ({self.status})"
