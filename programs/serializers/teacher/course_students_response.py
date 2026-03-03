from rest_framework import serializers


class TeacherCourseStudentItemSerializer(serializers.Serializer):
    person_id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    student_number = serializers.CharField(allow_blank=True)


class TeacherCourseStudentsResponseSerializer(serializers.Serializer):
    students = serializers.ListField(child=TeacherCourseStudentItemSerializer())
