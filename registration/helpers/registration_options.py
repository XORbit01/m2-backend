"""
Load options for registration step fields that require selection from predefined data.
Used to enrich question definitions in GET /registration/state/ so frontend can render selects.
"""

from datetime import datetime

from programs.models import Cohort, Major


def get_options_majors():
    """Return list of {value: id, label: "code - name"} for Major."""
    majors = Major.objects.all().order_by("code")
    return [{"value": m.id, "label": f"{m.code} - {m.name}"} for m in majors]


def get_options_cohort_years():
    """Return list of {value: academic_year, label: academic_year} for Cohort academic years."""
    years = (
        Cohort.objects.values_list("academic_year", flat=True)
        .distinct()
        .order_by("-academic_year")
    )
    return [{"value": y, "label": y} for y in years]


def get_options_graduation_years():
    """Return list of {value: year, label: year} for graduation year (e.g. last 30 years)."""
    current = datetime.now().year
    start = current - 30
    return [{"value": y, "label": str(y)} for y in range(current + 1, start - 1, -1)]


def get_options_for_source(source: str) -> list[dict]:
    """
    Return options list for a given options_source key.
    Used by registration state to enrich fields with type "select" and options_source.
    """
    if source == "majors":
        return get_options_majors()
    if source == "cohort_years":
        return get_options_cohort_years()
    if source == "graduation_years":
        return get_options_graduation_years()
    return []


def enrich_question_with_options(question_def: dict) -> dict:
    """
    Inject options into fields that have options_source (for select type).
    Mutates and returns the given dict; call with a copy if original must be preserved.
    """
    fields = question_def.get("fields")
    if not fields:
        return question_def
    for field in fields:
        source = field.get("options_source")
        if source:
            field["options"] = get_options_for_source(source)
    return question_def
