"""
Role detection and profile building for the /me endpoint.
Detects student, teacher, coordinator roles and builds role-specific profile data.
"""

from core.models import Person
from enrollment.models import Enrollment
from programs.helpers.coordinator import get_coordinated_major_ids
from programs.models import CourseOffering, Major
from profiles.models import AlumniProfile, GuestProfile, StudentProfile, TeacherProfile


def get_me_roles(person, user=None):
    """
    Return list of role strings for person: student, alumni, teacher, guest,
    coordinator, admin. Person can have multiple roles. Admin is added when
    user.is_staff.
    """
    if person is None and user is None:
        return []
    roles = []
    if person is not None:
        if StudentProfile.objects.filter(person=person).exists():
            roles.append("student")
        if AlumniProfile.objects.filter(person=person).exists():
            roles.append("alumni")
        if TeacherProfile.objects.filter(person=person).exists():
            roles.append("teacher")
        if GuestProfile.objects.filter(person=person).exists():
            roles.append("guest")
        if get_coordinated_major_ids(person):
            roles.append("coordinator")
    u = user if user is not None else (getattr(person, "user", None) if person else None)
    if u and getattr(u, "is_staff", False):
        roles.append("admin")
    return roles


def build_me_profile(person):
    """
    Build profile dict based on person's roles.
    Returns dict with full_name + role-specific fields (student, teacher, coordinator).
    """
    if person is None:
        return None

    profile = {"full_name": person.full_name}

    try:
        student = person.student_profile
        profile["student_number"] = student.student_number
        profile["current_status"] = student.current_status
        enrollments = list(
            Enrollment.objects.filter(student=person)
            .select_related("cohort", "major", "cohort__program")
            .order_by("-cohort__academic_year")
        )
        profile["enrollments"] = [
            {
                "id": e.id,
                "cohort_id": e.cohort_id,
                "cohort_academic_year": e.cohort.academic_year,
                "major_id": e.major_id,
                "major_code": e.major.code,
                "major_name": e.major.name,
                "program_name": e.cohort.program.name,
                "status": e.status,
            }
            for e in enrollments
        ]
        cohort_ids = [e.cohort_id for e in enrollments]
        if cohort_ids:
            offerings = (
                CourseOffering.objects.filter(cohort_id__in=cohort_ids)
                .select_related("course", "semester", "teacher")
                .order_by("semester__name", "course__code")
            )
            profile["courses"] = [
                {
                    "id": o.id,
                    "course_code": o.course.code,
                    "course_title": o.course.title,
                    "semester_name": o.semester.name,
                    "cohort_academic_year": o.cohort.academic_year,
                    "teacher_name": o.teacher.full_name if o.teacher else None,
                }
                for o in offerings
            ]
        else:
            profile["courses"] = []
    except StudentProfile.DoesNotExist:
        pass

    try:
        alumni = person.alumni_profile
        if "student_number" not in profile:
            profile["graduation_year"] = alumni.graduation_year
            profile["current_country"] = alumni.current_country
    except AlumniProfile.DoesNotExist:
        pass

    try:
        teacher = person.teacher_profile
        profile["title"] = teacher.title
        profile["department"] = teacher.department
        profile["is_supervisor"] = teacher.is_supervisor
        offerings = (
            CourseOffering.objects.filter(teacher=person)
            .select_related("course", "cohort", "semester")
            .order_by("-cohort__academic_year", "semester__name", "course__code")
        )
        profile["taught_courses"] = [
            {
                "id": o.id,
                "course_code": o.course.code,
                "course_title": o.course.title,
                "semester_name": o.semester.name,
                "cohort_academic_year": o.cohort.academic_year,
            }
            for o in offerings
        ]
    except TeacherProfile.DoesNotExist:
        pass

    major_ids = list(get_coordinated_major_ids(person))
    if major_ids:
        majors = Major.objects.filter(id__in=major_ids).order_by("code")
        profile["coordinated_majors"] = [
            {"id": m.id, "code": m.code, "name": m.name} for m in majors
        ]

    return profile
