"""
Create profiles and experiences from an accepted registration session.
Called when major coordinator accepts; maps session payload and base_role to
StudentProfile or AlumniProfile, and to Experience (internship, PhD, work).
"""

import logging
from datetime import date

from core.enums import ExperienceStatus, ExperienceType, StudentStatus
from experience.models import Experience
from institutions.models import Institution
from profiles.models import AlumniProfile, StudentProfile
from registration.enums import BaseRole

log = logging.getLogger(__name__)

# Default when registration does not collect the field (e.g. current_country for alumni)
ALUMNI_CURRENT_COUNTRY_DEFAULT = ""


def _parse_date(value):
    """Return date from string (YYYY-MM-DD) or None."""
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip()[:10])
    except (ValueError, TypeError):
        return None


def _get_institution_by_name(name):
    """Return Institution by name or None."""
    if not name or not str(name).strip():
        return None
    return Institution.objects.filter(name=str(name).strip()).first()


def _create_experiences_from_payload(session):
    """
    Create Experience records from payload.internships, payload.phd, payload.work.
    Only run when we have just created the profile to avoid duplicates.
    Internship: STAGE, status ONGOING (student) / COMPLETED (alumni).
    PhD: DOCTORATE, status ONGOING. Work: JOB, status ONGOING.
    """
    person = session.person
    payload = session.payload or {}
    base_role = session.base_role
    internship_status = (
        ExperienceStatus.ONGOING.value
        if base_role == BaseRole.STUDENT.value
        else ExperienceStatus.COMPLETED.value
    )

    for item in payload.get("internships") or []:
        inst = _get_institution_by_name(item.get("institution_name"))
        if not inst:
            log.warning(
                "Accepted session %s internship institution not found: %s",
                session.id,
                item.get("institution_name"),
            )
            continue
        title = (item.get("department") or "").strip() or "Internship"
        if len(title) > 255:
            title = title[:255]
        Experience.objects.create(
            person=person,
            type=ExperienceType.STAGE.value,
            status=internship_status,
            institution=inst,
            title=title,
            start_date=_parse_date(item.get("start_date")),
            end_date=_parse_date(item.get("end_date")),
        )

    for item in payload.get("phd") or []:
        inst = _get_institution_by_name(item.get("institution_name"))
        if not inst:
            log.warning(
                "Accepted session %s phd institution not found: %s",
                session.id,
                item.get("institution_name"),
            )
            continue
        title = (item.get("field") or "").strip() or "PhD"
        if len(title) > 255:
            title = title[:255]
        lab_name = (item.get("lab_name") or "").strip()[:255]
        Experience.objects.create(
            person=person,
            type=ExperienceType.DOCTORATE.value,
            status=ExperienceStatus.ONGOING.value,
            institution=inst,
            title=title,
            lab_name=lab_name,
            start_date=_parse_date(item.get("start_date")),
            end_date=_parse_date(item.get("end_date")),
        )

    for item in payload.get("work") or []:
        inst = _get_institution_by_name(item.get("institution_name"))
        if not inst:
            log.warning(
                "Accepted session %s work institution not found: %s",
                session.id,
                item.get("institution_name"),
            )
            continue
        title = (item.get("title") or "").strip() or "Work"
        if len(title) > 255:
            title = title[:255]
        Experience.objects.create(
            person=person,
            type=ExperienceType.JOB.value,
            status=ExperienceStatus.ONGOING.value,
            institution=inst,
            title=title,
            start_date=_parse_date(item.get("start_date")),
            end_date=_parse_date(item.get("end_date")),
        )


def create_profiles_from_accepted_session(session):
    """
    Create StudentProfile or AlumniProfile from an accepted RegistrationSession,
    then create Experience records (internship, PhD, work) from payload.
    Uses session.person, session.base_role, session.payload.
    Idempotent: if the profile already exists, it is not duplicated (get_or_create).
    Experiences are only created when the profile is first created.
    Returns the created or existing profile instance, or None if role/payload invalid.
    """
    if session.status != "ACCEPTED":
        return None
    person = session.person
    payload = session.payload or {}
    base_role = session.base_role
    profile_created = False

    if base_role == BaseRole.STUDENT.value:
        student = payload.get("student") or {}
        student_number = student.get("student_number")
        if not student_number:
            log.warning("Accepted session %s has no student.student_number", session.id)
            return None
        profile, profile_created = StudentProfile.objects.get_or_create(
            person=person,
            defaults={
                "student_number": student_number,
                "current_status": StudentStatus.ACTIVE.value,
            },
        )
        if profile_created:
            log.info("Created StudentProfile for person_id=%s", person.id)
        if profile_created:
            _create_experiences_from_payload(session)
        return profile

    if base_role == BaseRole.ALUMNI.value:
        alumni = payload.get("alumni") or {}
        graduation_year_raw = alumni.get("graduation_year")
        if graduation_year_raw is None or graduation_year_raw == "":
            log.warning("Accepted session %s has no alumni.graduation_year", session.id)
            return None
        try:
            graduation_year = int(graduation_year_raw)
        except (TypeError, ValueError):
            log.warning(
                "Accepted session %s invalid alumni.graduation_year: %s",
                session.id,
                graduation_year_raw,
            )
            return None
        profile, profile_created = AlumniProfile.objects.get_or_create(
            person=person,
            defaults={
                "graduation_year": graduation_year,
                "current_country": ALUMNI_CURRENT_COUNTRY_DEFAULT,
            },
        )
        if profile_created:
            log.info("Created AlumniProfile for person_id=%s", person.id)
        if profile_created:
            _create_experiences_from_payload(session)
        return profile

    log.warning("Accepted session %s unknown base_role=%s", session.id, base_role)
    return None
