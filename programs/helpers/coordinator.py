"""Helpers for major coordinator scope (programs, course offerings)."""

from programs.models import MajorCoordinator


def get_coordinated_major_ids(person):
    """Return set of major IDs that this person coordinates (major coordinator)."""
    if person is None:
        return set()
    ids = MajorCoordinator.objects.filter(coordinator=person).values_list(
        "major_id", flat=True
    )
    return set(ids)
