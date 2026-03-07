from django.urls import path

from options.api.v1.views import (
    AdminOptionsView,
    OptionsCohortsView,
    OptionsCoursesView,
    OptionsInstitutionTypesView,
    OptionsInstitutionsView,
    OptionsMajorsView,
    OptionsProgramsView,
    OptionsSemestersView,
)

app_name = "options"

urlpatterns = [
    path("majors/", OptionsMajorsView.as_view()),
    path("programs/", OptionsProgramsView.as_view()),
    path("cohorts/", OptionsCohortsView.as_view()),
    path("courses/", OptionsCoursesView.as_view()),
    path("semesters/", OptionsSemestersView.as_view()),
    path("institutions/", OptionsInstitutionsView.as_view()),
    path("institution-types/", OptionsInstitutionTypesView.as_view()),
    path("admin/", AdminOptionsView.as_view()),
]
