"""
Validate major_id: must be an existing Major pk.
"""


def validate_major_id(value) -> str | None:
    """
    Return None if value is valid (existing Major id), else return error message.
    """
    if value is None:
        return None
    try:
        pk = int(value)
    except (TypeError, ValueError):
        return "Invalid major."
    from programs.models import Major

    if not Major.objects.filter(pk=pk).exists():
        return "Invalid or unknown major."
    return None
