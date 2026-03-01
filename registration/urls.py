from django.urls import path

from registration.views import (
    RegistrationAnswerView,
    RegistrationStateView,
    RegistrationSubmitView,
)

app_name = "registration"

urlpatterns = [
    path("state/", RegistrationStateView.as_view(), name="state"),
    path("answer/", RegistrationAnswerView.as_view(), name="answer"),
    path("submit/", RegistrationSubmitView.as_view(), name="submit"),
]
