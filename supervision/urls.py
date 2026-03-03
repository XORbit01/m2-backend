from django.urls import path

from supervision.views import (
    StudentSupervisionCancelView,
    StudentSupervisionListCreateView,
    TeacherSupervisionApproveView,
    TeacherSupervisionListView,
    TeacherSupervisionRejectView,
)

app_name = "supervision"

urlpatterns = [
    path(
        "student/requests/",
        StudentSupervisionListCreateView.as_view(),
        name="student-supervision-requests",
    ),
    path(
        "student/requests/<int:supervision_id>/cancel/",
        StudentSupervisionCancelView.as_view(),
        name="student-supervision-cancel",
    ),
    path(
        "teacher/requests/",
        TeacherSupervisionListView.as_view(),
        name="teacher-supervision-requests",
    ),
    path(
        "teacher/requests/<int:supervision_id>/approve/",
        TeacherSupervisionApproveView.as_view(),
        name="teacher-supervision-approve",
    ),
    path(
        "teacher/requests/<int:supervision_id>/reject/",
        TeacherSupervisionRejectView.as_view(),
        name="teacher-supervision-reject",
    ),
]

