from django.urls import path

from institutions.api.admin_institutions.views import (
    AdminInstitutionDetailView,
    AdminInstitutionListCreateView,
)

app_name = "institutions"

urlpatterns = [
    path("admin/institutions/", AdminInstitutionListCreateView.as_view()),
    path(
        "admin/institutions/<int:institution_id>/",
        AdminInstitutionDetailView.as_view(),
    ),
]
