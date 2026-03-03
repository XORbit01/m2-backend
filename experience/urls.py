from django.urls import path

from experience.views import MyExperienceDetailView, MyExperiencesListCreateView

app_name = "experience"

urlpatterns = [
    path(
        "me/",
        MyExperiencesListCreateView.as_view(),
        name="my-experiences",
    ),
    path(
        "me/<int:experience_id>/",
        MyExperienceDetailView.as_view(),
        name="my-experience-detail",
    ),
]

