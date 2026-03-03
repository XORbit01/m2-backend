"""
Central registry for all accounts/auth views.
"""

from accounts.api.v1.admin.create_teacher.views import CreateTeacherView
from accounts.api.v1.admin.create_user.views import CreateUserView
from accounts.api.v1.login.views import LoginView
from accounts.api.v1.me.views import MeView
from accounts.api.v1.profile.views import ProfileSettingsView

__all__ = ["CreateTeacherView", "CreateUserView", "LoginView", "MeView", "ProfileSettingsView"]
