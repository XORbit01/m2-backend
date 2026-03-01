"""
Registration flow enums. Hardcoded step names for the decision tree.
"""

from django.db import models


class RegistrationStep(models.TextChoices):
    Q1_MASTER_STATUS = "Q1_MASTER_STATUS", "Q1 Master status"
    COLLECT_STUDENT_DATA = "COLLECT_STUDENT_DATA", "Collect student data"
    Q2_INTERNSHIP = "Q2_INTERNSHIP", "Q2 Internship (student)"
    COLLECT_INTERNSHIP = "COLLECT_INTERNSHIP", "Collect internship"
    COLLECT_ALUMNI_DATA = "COLLECT_ALUMNI_DATA", "Collect alumni data"
    Q2_INTERNSHIP_ALUMNI = "Q2_INTERNSHIP_ALUMNI", "Q2 Internship (alumni)"
    Q3_PHD = "Q3_PHD", "Q3 PhD"
    COLLECT_PHD = "COLLECT_PHD", "Collect PhD"
    Q4_WORK = "Q4_WORK", "Q4 Work"
    COLLECT_WORK = "COLLECT_WORK", "Collect work"
    SUBMIT = "SUBMIT", "Submit"


class BaseRole(models.TextChoices):
    STUDENT = "STUDENT", "Student"
    ALUMNI = "ALUMNI", "Alumni"


class RegistrationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SUBMITTED = "SUBMITTED", "Submitted"
