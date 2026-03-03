from django.urls import path

from programs.views import (
    CoordinatorAssignTeacherView,
    CoordinatorCohortsListView,
    CoordinatorOfferingsListView,
    CoordinatorStudentsListView,
    CoordinatorTeachersListView,
    TeacherCourseStudentsListView,
)

app_name = "programs"

urlpatterns = [
    path(
        "coordinator/offerings/",
        CoordinatorOfferingsListView.as_view(),
        name="coordinator-offerings",
    ),
    path(
        "coordinator/teachers/",
        CoordinatorTeachersListView.as_view(),
        name="coordinator-teachers",
    ),
    path(
        "coordinator/students/",
        CoordinatorStudentsListView.as_view(),
        name="coordinator-students",
    ),
    path(
        "coordinator/cohorts/",
        CoordinatorCohortsListView.as_view(),
        name="coordinator-cohorts",
    ),
    path(
        "coordinator/offerings/<int:offering_id>/assign/",
        CoordinatorAssignTeacherView.as_view(),
        name="coordinator-assign-teacher",
    ),
    path(
        "teacher/courses/<int:offering_id>/students/",
        TeacherCourseStudentsListView.as_view(),
        name="teacher-course-students",
    ),
]
