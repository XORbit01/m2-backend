"""
Shared enums for M2. All apps import from here.
"""

from django.db import models


class StudentStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    GRADUATED = "GRADUATED", "Graduated"
    SUSPENDED = "SUSPENDED", "Suspended"


class EnrollmentStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    COMPLETED = "COMPLETED", "Completed"
    DROPPED = "DROPPED", "Dropped"


class InstitutionType(models.TextChoices):
    UNIVERSITY = "UNIVERSITY", "University"
    LAB = "LAB", "Lab"
    COMPANY = "COMPANY", "Company"
    HOSPITAL = "HOSPITAL", "Hospital"
    OTHER = "OTHER", "Other"


class ExperienceType(models.TextChoices):
    STAGE = "STAGE", "Stage"
    DOCTORATE = "DOCTORATE", "Doctorate"
    RESEARCH = "RESEARCH", "Research"
    JOB = "JOB", "Job"
    OTHER = "OTHER", "Other"


class ExperienceStatus(models.TextChoices):
    PLANNED = "PLANNED", "Planned"
    ONGOING = "ONGOING", "Ongoing"
    COMPLETED = "COMPLETED", "Completed"
    STOPPED = "STOPPED", "Stopped"


class SupervisionStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"


class PostAudienceRole(models.TextChoices):
    GENERAL = "GENERAL", "General"
    STUDENTS = "STUDENTS", "Students"
    SUPERVISORS = "SUPERVISORS", "Supervisors"
    TEACHERS = "TEACHERS", "Teachers"
    ALUMNI = "ALUMNI", "Alumni"
    GUESTS = "GUESTS", "Guests"
