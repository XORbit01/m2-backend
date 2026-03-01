"""
Validate institution_name: must match an existing Institution by name.
"""


def validate_institution_name(value) -> str | None:
    """
    Return None if value is valid (existing Institution name or empty skip), else return error message.
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    name = value.strip() if isinstance(value, str) else str(value)
    from institutions.models import Institution

    if not Institution.objects.filter(name=name).exists():
        return "Unknown institution."
    return None
