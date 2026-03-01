from django.urls import path

from registration.views import (CoordinatorAcceptView,
                                CoordinatorPendingListView,
                                CoordinatorRejectView, RegistrationAnswerView,
                                RegistrationStateView, RegistrationSubmitView)

app_name = "registration"

urlpatterns = [
    path("state/", RegistrationStateView.as_view(), name="state"),
    path("answer/", RegistrationAnswerView.as_view(), name="answer"),
    path("submit/", RegistrationSubmitView.as_view(), name="submit"),
    path(
        "coordinator/pending/",
        CoordinatorPendingListView.as_view(),
        name="coordinator-pending",
    ),
    path(
        "coordinator/<int:session_id>/accept/",
        CoordinatorAcceptView.as_view(),
        name="coordinator-accept",
    ),
    path(
        "coordinator/<int:session_id>/reject/",
        CoordinatorRejectView.as_view(),
        name="coordinator-reject",
    ),
]
