from django.urls import path

from programs.api.v1.admin.cohorts.views import (
    AdminCohortDetailView,
    AdminCohortListCreateView,
)
from programs.api.v1.admin.courses.views import (
    AdminCourseDetailView,
    AdminCourseListCreateView,
)
from programs.api.v1.admin.major_coordinators.views import (
    AdminMajorCoordinatorAssignView,
    AdminMajorCoordinatorRemoveView,
)
from programs.api.v1.admin.majors.views import (
    AdminMajorDetailView,
    AdminMajorListCreateView,
)
from programs.api.v1.admin.offerings.views import (
    AdminOfferingDetailView,
    AdminOfferingListCreateView,
)
from programs.api.v1.admin.programs.views import (
    AdminProgramDetailView,
    AdminProgramListCreateView,
)
from programs.api.v1.admin.semesters.views import (
    AdminSemesterDetailView,
    AdminSemesterListCreateView,
)
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
    path("admin/majors/", AdminMajorListCreateView.as_view()),
    path("admin/majors/<int:major_id>/", AdminMajorDetailView.as_view()),
    path(
        "admin/majors/<int:major_id>/coordinators/",
        AdminMajorCoordinatorAssignView.as_view(),
    ),
    path(
        "admin/majors/<int:major_id>/coordinators/<int:person_id>/",
        AdminMajorCoordinatorRemoveView.as_view(),
    ),
    path("admin/programs/", AdminProgramListCreateView.as_view()),
    path("admin/programs/<int:program_id>/", AdminProgramDetailView.as_view()),
    path("admin/cohorts/", AdminCohortListCreateView.as_view()),
    path("admin/cohorts/<int:cohort_id>/", AdminCohortDetailView.as_view()),
    path("admin/courses/", AdminCourseListCreateView.as_view()),
    path("admin/courses/<int:course_id>/", AdminCourseDetailView.as_view()),
    path("admin/semesters/", AdminSemesterListCreateView.as_view()),
    path("admin/semesters/<int:semester_id>/", AdminSemesterDetailView.as_view()),
    path("admin/offerings/", AdminOfferingListCreateView.as_view()),
    path("admin/offerings/<int:offering_id>/", AdminOfferingDetailView.as_view()),
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
