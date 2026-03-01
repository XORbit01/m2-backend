"""
Helpers for major coordinator verification of submitted registrations.
"""

from programs.models import MajorCoordinator
from registration.enums import RegistrationStatus
from registration.models import RegistrationSession


def get_coordinated_major_ids(person):
    """Return set of major IDs that this person coordinates (major coordinator)."""
    if person is None:
        return set()
    ids = MajorCoordinator.objects.filter(coordinator=person).values_list(
        "major_id", flat=True
    )
    return set(ids)


def get_session_major_id(session):
    """Return major_id from session payload (student or alumni data), or None."""
    payload = session.payload or {}
    student = payload.get("student") or {}
    alumni = payload.get("alumni") or {}
    return student.get("major_id") or alumni.get("major_id")


def can_coordinator_verify_session(person, session):
    """
    Return True if person is a coordinator for the session's major
    and session is SUBMITTED (awaiting verification).
    """
    if person is None or session.status != RegistrationStatus.SUBMITTED.value:
        return False
    major_id = get_session_major_id(session)
    if major_id is None:
        return False
    coordinated = get_coordinated_major_ids(person)
    return major_id in coordinated
