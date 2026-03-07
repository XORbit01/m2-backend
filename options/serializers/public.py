"""Public options serializers for dropdowns."""

from rest_framework import serializers


class OptionMajorItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()


class OptionProgramItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    university = serializers.CharField()
    degree_level = serializers.CharField()
    major_id = serializers.IntegerField(allow_null=True)
    major_code = serializers.CharField(allow_null=True)


class OptionCohortItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    program_id = serializers.IntegerField()
    program_name = serializers.CharField()
    academic_year = serializers.CharField()
    major_id = serializers.IntegerField(allow_null=True)
    major_code = serializers.CharField(allow_null=True)


class OptionCourseItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    program_id = serializers.IntegerField()
    program_name = serializers.CharField()
    code = serializers.CharField()
    title = serializers.CharField()
    major_id = serializers.IntegerField(allow_null=True)
    major_code = serializers.CharField(allow_null=True)


class OptionSemesterItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    cohort_id = serializers.IntegerField()
    cohort_academic_year = serializers.CharField()
    program_name = serializers.CharField()
    name = serializers.CharField()


class OptionInstitutionItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    country = serializers.CharField()
    type = serializers.CharField()
    website = serializers.URLField()


class OptionInstitutionTypeItemSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class OptionTeacherItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="person_id, use as teacher_id in offering")
    name = serializers.CharField()
    email = serializers.EmailField()
    title = serializers.CharField()
    department = serializers.CharField()


class OptionsMajorsResponseSerializer(serializers.Serializer):
    majors = serializers.ListField(child=OptionMajorItemSerializer())


class OptionsProgramsResponseSerializer(serializers.Serializer):
    programs = serializers.ListField(child=OptionProgramItemSerializer())


class OptionsCohortsResponseSerializer(serializers.Serializer):
    cohorts = serializers.ListField(child=OptionCohortItemSerializer())


class OptionsCoursesResponseSerializer(serializers.Serializer):
    courses = serializers.ListField(child=OptionCourseItemSerializer())


class OptionsSemestersResponseSerializer(serializers.Serializer):
    semesters = serializers.ListField(child=OptionSemesterItemSerializer())


class OptionsInstitutionsResponseSerializer(serializers.Serializer):
    institutions = serializers.ListField(child=OptionInstitutionItemSerializer())


class OptionsInstitutionTypesResponseSerializer(serializers.Serializer):
    institution_types = serializers.ListField(child=OptionInstitutionTypeItemSerializer())


class OptionsTeachersResponseSerializer(serializers.Serializer):
    teachers = serializers.ListField(child=OptionTeacherItemSerializer())


class AdminOptionsResponseSerializer(serializers.Serializer):
    majors = serializers.ListField(child=OptionMajorItemSerializer())
    programs = serializers.ListField(child=OptionProgramItemSerializer())
    cohorts = serializers.ListField(child=OptionCohortItemSerializer())
    courses = serializers.ListField(child=OptionCourseItemSerializer())
    semesters = serializers.ListField(child=OptionSemesterItemSerializer())
    institutions = serializers.ListField(child=OptionInstitutionItemSerializer())
    institution_types = serializers.ListField(child=OptionInstitutionTypeItemSerializer())
    teachers = serializers.ListField(child=OptionTeacherItemSerializer())
