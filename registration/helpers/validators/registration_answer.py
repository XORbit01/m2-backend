"""
Orchestrates registration answer validation: delegates to major/institution validators per step.
Returns None if valid, or a dict of field_key -> error message for 400 response.
"""

from registration.enums import RegistrationStep
from registration.helpers.validators.institution import \
    validate_institution_name
from registration.helpers.validators.major import validate_major_id


def validate_registration_answer(current_step: str, data: dict) -> dict | None:
    """
    Validate step-specific answer data. ID fields must exist in DB;
    institution is by name and must match an existing Institution.

    Returns None if valid, or a dict of errors for 400 response.
    """
    errors = {}

    if current_step == RegistrationStep.COLLECT_STUDENT_DATA.value:
        student = data.get("student_data")
        if student and isinstance(student, dict):
            err = validate_major_id(student.get("major_id"))
            if err:
                errors["student_data.major_id"] = err

    if current_step == RegistrationStep.COLLECT_ALUMNI_DATA.value:
        alumni = data.get("alumni_data")
        if alumni and isinstance(alumni, dict):
            err = validate_major_id(alumni.get("major_id"))
            if err:
                errors["alumni_data.major_id"] = err

    if current_step == RegistrationStep.COLLECT_INTERNSHIP.value:
        internship = data.get("internship_data")
        if internship and isinstance(internship, dict):
            err = validate_institution_name(internship.get("institution_name"))
            if err:
                errors["internship_data.institution_name"] = err

    if current_step == RegistrationStep.Q2_INTERNSHIP.value:
        if data.get("has_internship") is True:
            internship = data.get("internship_data")
            if internship and isinstance(internship, dict):
                err = validate_institution_name(internship.get("institution_name"))
                if err:
                    errors["internship_data.institution_name"] = err

    if current_step == RegistrationStep.Q2_INTERNSHIP_ALUMNI.value:
        if data.get("had_internship") is True:
            internship = data.get("internship_data")
            if internship and isinstance(internship, dict):
                err = validate_institution_name(internship.get("institution_name"))
                if err:
                    errors["internship_data.institution_name"] = err

    if current_step == RegistrationStep.COLLECT_PHD.value:
        phd = data.get("phd_data")
        if phd and isinstance(phd, dict):
            err = validate_institution_name(phd.get("institution_name"))
            if err:
                errors["phd_data.institution_name"] = err

    if current_step == RegistrationStep.Q3_PHD.value:
        if data.get("is_phd_student") is True:
            phd = data.get("phd_data")
            if phd and isinstance(phd, dict):
                err = validate_institution_name(phd.get("institution_name"))
                if err:
                    errors["phd_data.institution_name"] = err

    if current_step == RegistrationStep.COLLECT_WORK.value:
        work = data.get("work_data")
        if work and isinstance(work, dict):
            err = validate_institution_name(work.get("institution_name"))
            if err:
                errors["work_data.institution_name"] = err

    if current_step == RegistrationStep.Q4_WORK.value:
        if data.get("is_working") is True:
            work = data.get("work_data")
            if work and isinstance(work, dict):
                err = validate_institution_name(work.get("institution_name"))
                if err:
                    errors["work_data.institution_name"] = err

    return errors if errors else None
