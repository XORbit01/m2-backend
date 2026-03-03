from rest_framework import serializers


class MeEnrollmentItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    cohort_id = serializers.IntegerField()
    cohort_academic_year = serializers.CharField()
    major_id = serializers.IntegerField()
    major_code = serializers.CharField()
    major_name = serializers.CharField()
    program_name = serializers.CharField()
    status = serializers.CharField()


class MeCourseItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    course_code = serializers.CharField()
    course_title = serializers.CharField()
    semester_name = serializers.CharField()
    cohort_academic_year = serializers.CharField()
    teacher_name = serializers.CharField(allow_null=True)


class MeTaughtCourseItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    course_code = serializers.CharField()
    course_title = serializers.CharField()
    semester_name = serializers.CharField()
    cohort_academic_year = serializers.CharField()


class MeCoordinatedMajorItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()


class MeProfileSerializer(serializers.Serializer):
    full_name = serializers.CharField()

    student_number = serializers.CharField(required=False)
    current_status = serializers.CharField(required=False)
    enrollments = serializers.ListField(
        child=MeEnrollmentItemSerializer(), required=False
    )
    courses = serializers.ListField(child=MeCourseItemSerializer(), required=False)

    graduation_year = serializers.IntegerField(required=False)
    current_country = serializers.CharField(required=False)

    title = serializers.CharField(required=False)
    department = serializers.CharField(required=False)
    is_supervisor = serializers.BooleanField(required=False)
    taught_courses = serializers.ListField(
        child=MeTaughtCourseItemSerializer(), required=False
    )

    coordinated_majors = serializers.ListField(
        child=MeCoordinatedMajorItemSerializer(), required=False
    )


class MeResponseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    email = serializers.EmailField()
    registration_complete = serializers.BooleanField()
    current_step = serializers.CharField(allow_null=True)
    person_id = serializers.IntegerField(allow_null=True)
    roles = serializers.ListField(child=serializers.CharField())
    profile = MeProfileSerializer(allow_null=True)
