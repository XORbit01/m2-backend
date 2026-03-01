"""
Registration decision tree state machine. Hardcoded transitions.
"""

from registration.enums import BaseRole, RegistrationStep


def get_next_step(
    current_step: str, answer: dict, base_role: str | None = None
) -> RegistrationStep | None:
    """
    Return the next step given current step and answer payload.
    base_role is used to branch after COLLECT_INTERNSHIP (alumni -> Q3_PHD, student -> Q4_WORK).
    Returns None if transition is invalid or already at SUBMIT.
    """
    step = getattr(RegistrationStep, current_step, None)
    if step is None or step == RegistrationStep.SUBMIT:
        return None

    if step == RegistrationStep.Q1_MASTER_STATUS:
        finished_master = answer.get("finished_master")
        if finished_master is True:
            return RegistrationStep.COLLECT_ALUMNI_DATA
        if finished_master is False:
            return RegistrationStep.COLLECT_STUDENT_DATA
        return None

    if step == RegistrationStep.COLLECT_STUDENT_DATA:
        return RegistrationStep.Q2_INTERNSHIP

    if step == RegistrationStep.Q2_INTERNSHIP:
        if answer.get("has_internship") is True:
            return RegistrationStep.COLLECT_INTERNSHIP
        return RegistrationStep.Q4_WORK

    if step == RegistrationStep.COLLECT_INTERNSHIP:
        # Alumni path: after internship go to Q3_PHD; student path: go to Q4_WORK
        if base_role == BaseRole.ALUMNI.value:
            return RegistrationStep.Q3_PHD
        return RegistrationStep.Q4_WORK

    if step == RegistrationStep.COLLECT_ALUMNI_DATA:
        return RegistrationStep.Q2_INTERNSHIP_ALUMNI

    if step == RegistrationStep.Q2_INTERNSHIP_ALUMNI:
        if answer.get("had_internship") is True:
            return RegistrationStep.COLLECT_INTERNSHIP
        return RegistrationStep.Q3_PHD

    if step == RegistrationStep.Q3_PHD:
        if answer.get("is_phd_student") is True:
            return RegistrationStep.COLLECT_PHD
        return RegistrationStep.Q4_WORK

    if step == RegistrationStep.COLLECT_PHD:
        return RegistrationStep.Q4_WORK

    if step == RegistrationStep.Q4_WORK:
        if answer.get("is_working") is True:
            return RegistrationStep.COLLECT_WORK
        return RegistrationStep.SUBMIT

    if step == RegistrationStep.COLLECT_WORK:
        return RegistrationStep.SUBMIT

    return None


def get_base_role_from_q1(answer: dict) -> BaseRole | None:
    """Return BaseRole from Q1 answer."""
    finished_master = answer.get("finished_master")
    if finished_master is True:
        return BaseRole.ALUMNI
    if finished_master is False:
        return BaseRole.STUDENT
    return None


def get_required_answer_key(current_step: str) -> str | tuple[str, ...] | None:
    """
    Return the request key(s) required for the current step.
    Step is only valid if the corresponding key is present in the request.
    Returns None for steps that don't require a specific key (e.g. SUBMIT).
    """
    required = {
        RegistrationStep.Q1_MASTER_STATUS.value: "finished_master",
        RegistrationStep.COLLECT_STUDENT_DATA.value: "student_data",
        RegistrationStep.COLLECT_ALUMNI_DATA.value: "alumni_data",
        RegistrationStep.Q2_INTERNSHIP.value: ("has_internship",),
        RegistrationStep.Q2_INTERNSHIP_ALUMNI.value: ("had_internship",),
        RegistrationStep.COLLECT_INTERNSHIP.value: "internship_data",
        RegistrationStep.Q3_PHD.value: ("is_phd_student",),
        RegistrationStep.COLLECT_PHD.value: "phd_data",
        RegistrationStep.Q4_WORK.value: ("is_working",),
        RegistrationStep.COLLECT_WORK.value: "work_data",
    }
    return required.get(current_step)
