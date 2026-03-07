"""
Hardcoded question definitions per registration step.
Single source of truth for question type, label, options, and fields.
"""

from registration.enums import RegistrationStep

# Question type constants for frontend
QUESTION_TYPE_YES_NO = "yes_no"
QUESTION_TYPE_SELECT = "select"
QUESTION_TYPE_MULTIPLE_CHOICE = "multiple_choice"
QUESTION_TYPE_TEXT = "text"
QUESTION_TYPE_FREE_TEXT = "free_text"
QUESTION_TYPE_NUMBER = "number"
QUESTION_TYPE_DATE = "date"
QUESTION_TYPE_OBJECT = "object"
QUESTION_TYPE_SUBMIT = "submit"

# Internship / PhD / Work shared field definitions (institution by name, not ID)
INTERNSHIP_FIELDS = [
    {"key": "institution_name", "type": "text", "label": "Institution", "required": True},
    {"key": "department", "type": "text", "label": "Department", "required": True},
    {"key": "country", "type": "text", "label": "Country", "required": True},
    {"key": "start_date", "type": "date", "label": "Start date", "required": True},
    {"key": "end_date", "type": "date", "label": "End date", "required": False},
]

PHD_FIELDS = [
    {"key": "institution_name", "type": "text", "label": "Institution", "required": True},
    {"key": "field", "type": "text", "label": "Field", "required": True},
    {"key": "lab_name", "type": "text", "label": "Lab name", "required": True},
    {"key": "start_date", "type": "date", "label": "Start date", "required": True},
    {"key": "end_date", "type": "date", "label": "End date", "required": False},
]

WORK_FIELDS = [
    {"key": "institution_name", "type": "text", "label": "Institution", "required": True},
    {"key": "title", "type": "text", "label": "Title", "required": True},
    {"key": "country", "type": "text", "label": "Country", "required": True},
    {"key": "start_date", "type": "date", "label": "Start date", "required": True},
    {"key": "end_date", "type": "date", "label": "End date", "required": False},
]

STEP_DEFINITIONS = {
    RegistrationStep.Q1_MASTER_STATUS.value: {
        "question_key": "finished_master",
        "question_type": QUESTION_TYPE_YES_NO,
        "label": "Have you already completed a Master's degree?",
        "description": None,
        "required": True,
        "options": [
            {"value": False, "label": "No (current student)"},
            {"value": True, "label": "Yes (alumni)"},
        ],
    },
    RegistrationStep.COLLECT_STUDENT_DATA.value: {
        "question_key": "student_data",
        "question_type": QUESTION_TYPE_OBJECT,
        "label": "Student information",
        "description": None,
        "required": True,
        "fields": [
            {
                "key": "major_id",
                "type": QUESTION_TYPE_SELECT,
                "label": "Major",
                "required": True,
                "options_source": "majors",
                "value_type": "number",
            },
            {"key": "student_number", "type": "text", "label": "Student number", "required": True},
            {
                "key": "cohort_year",
                "type": QUESTION_TYPE_SELECT,
                "label": "Cohort year",
                "required": True,
                "options_source": "cohort_years",
                "value_type": "string",
            },
        ],
    },
    RegistrationStep.COLLECT_ALUMNI_DATA.value: {
        "question_key": "alumni_data",
        "question_type": QUESTION_TYPE_OBJECT,
        "label": "Alumni information",
        "description": None,
        "required": True,
        "fields": [
            {
                "key": "graduation_year",
                "type": QUESTION_TYPE_SELECT,
                "label": "Graduation year",
                "required": True,
                "options_source": "graduation_years",
                "value_type": "string",
            },
            {
                "key": "major_id",
                "type": QUESTION_TYPE_SELECT,
                "label": "Major",
                "required": True,
                "options_source": "majors",
                "value_type": "number",
            },
        ],
    },
    RegistrationStep.Q2_INTERNSHIP.value: {
        "question_key": "has_internship",
        "question_type": QUESTION_TYPE_YES_NO,
        "label": "Do you have an internship (current student)?",
        "description": "If yes, you will be asked to provide internship details.",
        "required": True,
        "options": [
            {"value": False, "label": "No"},
            {"value": True, "label": "Yes"},
        ],
        "nested_object_key": "internship_data",
        "nested_fields": INTERNSHIP_FIELDS,
    },
    RegistrationStep.Q2_INTERNSHIP_ALUMNI.value: {
        "question_key": "had_internship",
        "question_type": QUESTION_TYPE_YES_NO,
        "label": "Did you have an internship (alumni)?",
        "description": "If yes, you will be asked to provide internship details.",
        "required": True,
        "options": [
            {"value": False, "label": "No"},
            {"value": True, "label": "Yes"},
        ],
        "nested_object_key": "internship_data",
        "nested_fields": INTERNSHIP_FIELDS,
    },
    RegistrationStep.COLLECT_INTERNSHIP.value: {
        "question_key": "internship_data",
        "question_type": QUESTION_TYPE_OBJECT,
        "label": "Internship details",
        "description": None,
        "required": True,
        "fields": INTERNSHIP_FIELDS,
    },
    RegistrationStep.Q3_PHD.value: {
        "question_key": "is_phd_student",
        "question_type": QUESTION_TYPE_YES_NO,
        "label": "Are you a PhD student?",
        "description": "If yes, you will be asked to provide PhD details.",
        "required": True,
        "options": [
            {"value": False, "label": "No"},
            {"value": True, "label": "Yes"},
        ],
        "nested_object_key": "phd_data",
        "nested_fields": PHD_FIELDS,
    },
    RegistrationStep.COLLECT_PHD.value: {
        "question_key": "phd_data",
        "question_type": QUESTION_TYPE_OBJECT,
        "label": "PhD details",
        "description": None,
        "required": True,
        "fields": PHD_FIELDS,
    },
    RegistrationStep.Q4_WORK.value: {
        "question_key": "is_working",
        "question_type": QUESTION_TYPE_YES_NO,
        "label": "Are you currently working?",
        "description": "If yes, you will be asked to provide work details.",
        "required": True,
        "options": [
            {"value": False, "label": "No"},
            {"value": True, "label": "Yes"},
        ],
        "nested_object_key": "work_data",
        "nested_fields": WORK_FIELDS,
    },
    RegistrationStep.COLLECT_WORK.value: {
        "question_key": "work_data",
        "question_type": QUESTION_TYPE_OBJECT,
        "label": "Work details",
        "description": None,
        "required": True,
        "fields": WORK_FIELDS,
    },
    RegistrationStep.SUBMIT.value: {
        "question_key": None,
        "question_type": QUESTION_TYPE_SUBMIT,
        "label": "Submit registration",
        "description": "Review and submit your registration.",
        "required": False,
    },
}


def get_question_definition(step: str) -> dict | None:
    """
    Return the question definition for the given step.
    step: RegistrationStep value (e.g. Q1_MASTER_STATUS, SUBMIT).
    Returns a dict with question_key, question_type, label, and type-specific keys (options, fields).
    Returns None if step is unknown.
    """
    return STEP_DEFINITIONS.get(step)
