"""Public and admin options views for dropdowns."""

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.enums import InstitutionType
from institutions.models import Institution
from programs.models import Cohort, Course, Major, Program, Semester
from profiles.models import TeacherProfile

from options.serializers.public import (
    AdminOptionsResponseSerializer,
    OptionsCohortsResponseSerializer,
    OptionsCoursesResponseSerializer,
    OptionsInstitutionTypesResponseSerializer,
    OptionsInstitutionsResponseSerializer,
    OptionsMajorsResponseSerializer,
    OptionsProgramsResponseSerializer,
    OptionsSemestersResponseSerializer,
    OptionsTeachersResponseSerializer,
)


def _major_item(major):
    return {"id": major.id, "code": major.code, "name": major.name}


def _program_item(prog):
    return {
        "id": prog.id,
        "name": prog.name,
        "university": prog.university,
        "degree_level": prog.degree_level,
        "major_id": prog.major_id,
        "major_code": prog.major.code if prog.major else None,
    }


def _cohort_item(cohort):
    return {
        "id": cohort.id,
        "program_id": cohort.program_id,
        "program_name": cohort.program.name,
        "academic_year": cohort.academic_year,
        "major_id": cohort.program.major_id if cohort.program else None,
        "major_code": cohort.program.major.code if cohort.program and cohort.program.major else None,
    }


def _course_item(course):
    return {
        "id": course.id,
        "program_id": course.program_id,
        "program_name": course.program.name,
        "code": course.code,
        "title": course.title,
        "major_id": course.program.major_id if course.program else None,
        "major_code": course.program.major.code if course.program and course.program.major else None,
    }


def _semester_item(sem):
    return {
        "id": sem.id,
        "cohort_id": sem.cohort_id,
        "cohort_academic_year": sem.cohort.academic_year,
        "program_name": sem.cohort.program.name,
        "name": sem.name,
    }


def _institution_item(inst):
    return {
        "id": inst.id,
        "name": inst.name,
        "country": inst.country,
        "type": inst.type,
        "website": inst.website or "",
    }


def _institution_types():
    return [{"value": t[0], "label": t[1]} for t in InstitutionType.choices]


def _teacher_item(t):
    return {
        "id": t.person_id,
        "name": t.person.full_name,
        "email": t.person.email,
        "title": t.title,
        "department": t.department,
    }


class OptionsMajorsView(APIView):
    """GET /api/v1/options/majors/ - Public. Returns majors for dropdowns."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: OptionsMajorsResponseSerializer})
    def get(self, request):
        majors = Major.objects.all().order_by("code")
        data = {"majors": [_major_item(m) for m in majors]}
        ser = OptionsMajorsResponseSerializer(data=data)
        ser.is_valid(raise_exception=True)
        return Response(ser.data)


class OptionsProgramsView(APIView):
    """GET /api/v1/options/programs/ - Public. Returns programs for dropdowns."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: OptionsProgramsResponseSerializer})
    def get(self, request):
        programs = Program.objects.all().select_related("major").order_by("name")
        data = {"programs": [_program_item(p) for p in programs]}
        ser = OptionsProgramsResponseSerializer(data=data)
        ser.is_valid(raise_exception=True)
        return Response(ser.data)


class OptionsCohortsView(APIView):
    """GET /api/v1/options/cohorts/ - Public. Returns cohorts for dropdowns."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: OptionsCohortsResponseSerializer})
    def get(self, request):
        cohorts = Cohort.objects.select_related("program", "program__major").order_by(
            "-academic_year", "program__name"
        )
        data = {"cohorts": [_cohort_item(c) for c in cohorts]}
        ser = OptionsCohortsResponseSerializer(data=data)
        ser.is_valid(raise_exception=True)
        return Response(ser.data)


class OptionsCoursesView(APIView):
    """GET /api/v1/options/courses/ - Public. Returns courses for dropdowns."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: OptionsCoursesResponseSerializer})
    def get(self, request):
        courses = Course.objects.select_related("program", "program__major").order_by(
            "program__name", "code"
        )
        data = {"courses": [_course_item(c) for c in courses]}
        ser = OptionsCoursesResponseSerializer(data=data)
        ser.is_valid(raise_exception=True)
        return Response(ser.data)


class OptionsSemestersView(APIView):
    """GET /api/v1/options/semesters/ - Public. Returns semesters for dropdowns."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: OptionsSemestersResponseSerializer})
    def get(self, request):
        semesters = Semester.objects.select_related("cohort", "cohort__program").order_by(
            "cohort__academic_year", "name"
        )
        data = {"semesters": [_semester_item(s) for s in semesters]}
        ser = OptionsSemestersResponseSerializer(data=data)
        ser.is_valid(raise_exception=True)
        return Response(ser.data)


class OptionsInstitutionsView(APIView):
    """GET /api/v1/options/institutions/ - Public. Returns institutions for dropdowns."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: OptionsInstitutionsResponseSerializer})
    def get(self, request):
        institutions = Institution.objects.all().order_by("name")
        data = {"institutions": [_institution_item(i) for i in institutions]}
        ser = OptionsInstitutionsResponseSerializer(data=data)
        ser.is_valid(raise_exception=True)
        return Response(ser.data)


class OptionsInstitutionTypesView(APIView):
    """GET /api/v1/options/institution-types/ - Public. Returns institution type enum."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: OptionsInstitutionTypesResponseSerializer})
    def get(self, request):
        data = {"institution_types": _institution_types()}
        ser = OptionsInstitutionTypesResponseSerializer(data=data)
        ser.is_valid(raise_exception=True)
        return Response(ser.data)


class AdminOptionsView(APIView):
    """
    GET /api/v1/options/admin/
    Admin only. Returns all options in one call (majors, programs, cohorts,
    courses, semesters, institutions, institution_types, teachers).
    """

    permission_classes = [IsAdminUser]

    @extend_schema(responses={200: AdminOptionsResponseSerializer})
    def get(self, request):
        majors = Major.objects.all().order_by("code")
        programs = Program.objects.all().select_related("major").order_by("name")
        cohorts = Cohort.objects.select_related("program", "program__major").order_by(
            "-academic_year", "program__name"
        )
        courses = Course.objects.select_related("program", "program__major").order_by(
            "program__name", "code"
        )
        semesters = Semester.objects.select_related("cohort", "cohort__program").order_by(
            "cohort__academic_year", "name"
        )
        institutions = Institution.objects.all().order_by("name")
        teachers = TeacherProfile.objects.select_related("person").order_by(
            "person__full_name"
        )

        data = {
            "majors": [_major_item(m) for m in majors],
            "programs": [_program_item(p) for p in programs],
            "cohorts": [_cohort_item(c) for c in cohorts],
            "courses": [_course_item(c) for c in courses],
            "semesters": [_semester_item(s) for s in semesters],
            "institutions": [_institution_item(i) for i in institutions],
            "institution_types": _institution_types(),
            "teachers": [_teacher_item(t) for t in teachers],
        }
        ser = AdminOptionsResponseSerializer(data=data)
        ser.is_valid(raise_exception=True)
        return Response(ser.data)
