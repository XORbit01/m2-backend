"""
Central registry for supervision views.
"""

from supervision.api.v1.student.views import (
    StudentSupervisionCancelView,
    StudentSupervisionListCreateView,
)
from supervision.api.v1.teacher.views import (
    TeacherSupervisionListView,
    TeacherSupervisionApproveView,
    TeacherSupervisionRejectView,
)

__all__ = [
    "StudentSupervisionCancelView",
    "StudentSupervisionListCreateView",
    "TeacherSupervisionApproveView",
    "TeacherSupervisionListView",
    "TeacherSupervisionRejectView",
]

