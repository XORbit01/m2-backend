from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.api.v1.admin.users.views import (
    AdminUserListCreateView,
    AdminUserDetailView,
)
from accounts.views import (
    CreateTeacherView,
    GuestRegisterView,
    LoginView,
    MeView,
    ProfileSettingsView,
)

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/guest/", GuestRegisterView.as_view(), name="register-guest"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("profile/", ProfileSettingsView.as_view(), name="profile-settings"),
    path("admin/users/", AdminUserListCreateView.as_view(), name="admin-users-list-create"),
    path(
        "admin/users/<int:user_id>/",
        AdminUserDetailView.as_view(),
        name="admin-users-detail",
    ),
    path("admin/teachers/", CreateTeacherView.as_view(), name="admin-create-teacher"),
]
