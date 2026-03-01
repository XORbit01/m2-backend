from django.db import models

from core.models import Person
from programs.models import Course, Semester


class CourseResult(models.Model):
    student = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="course_results")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="results")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="course_results")
    grade = models.DecimalField(max_digits=5, decimal_places=2)
    passed = models.BooleanField()

    class Meta:
        db_table = "academic_course_result"

    def __str__(self):
        return f"{self.student} - {self.course}: {self.grade}"
