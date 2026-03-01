from django.db import models

from core.models import Person


class Major(models.Model):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "programs_major"

    def __str__(self):
        return self.name


class MajorCoordinator(models.Model):
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name="coordinators")
    coordinator = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="coordinated_majors")
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "programs_major_coordinator"

    def __str__(self):
        return f"{self.major} - {self.coordinator}"


class Program(models.Model):
    name = models.CharField(max_length=255)
    university = models.CharField(max_length=255)
    degree_level = models.CharField(max_length=64)

    class Meta:
        db_table = "programs_program"

    def __str__(self):
        return self.name


class Cohort(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="cohorts")
    academic_year = models.CharField(max_length=32)

    class Meta:
        db_table = "programs_cohort"

    def __str__(self):
        return f"{self.program} {self.academic_year}"


class Course(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="courses")
    code = models.CharField(max_length=64)
    title = models.CharField(max_length=255)

    class Meta:
        db_table = "programs_course"

    def __str__(self):
        return f"{self.code} - {self.title}"


class Semester(models.Model):
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name="semesters")
    name = models.CharField(max_length=64)

    class Meta:
        db_table = "programs_semester"

    def __str__(self):
        return f"{self.cohort} - {self.name}"


class CourseOffering(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="offerings")
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name="course_offerings")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="course_offerings")
    teacher = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="taught_offerings")

    class Meta:
        db_table = "programs_course_offering"

    def __str__(self):
        return f"{self.course} - {self.semester}"
