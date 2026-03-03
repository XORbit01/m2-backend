"""
Central registry for programs views.
"""

from programs.api.v1.coordinator.views import (
    CoordinatorAssignTeacherView,
    CoordinatorCohortsListView,
    CoordinatorOfferingsListView,
    CoordinatorStudentsListView,
    CoordinatorTeachersListView,
)
from programs.api.v1.teacher.views import TeacherCourseStudentsListView

__all__ = [
    "CoordinatorAssignTeacherView",
    "CoordinatorCohortsListView",
    "CoordinatorOfferingsListView",
    "CoordinatorStudentsListView",
    "CoordinatorTeachersListView",
    "TeacherCourseStudentsListView",
]
