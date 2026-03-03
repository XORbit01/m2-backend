from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import (
    CreateTeacherView,
    CreateUserView,
    LoginView,
    MeView,
    ProfileSettingsView,
)

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("profile/", ProfileSettingsView.as_view(), name="profile-settings"),
    path("admin/users/", CreateUserView.as_view(), name="admin-create-user"),
    path("admin/teachers/", CreateTeacherView.as_view(), name="admin-create-teacher"),
]
