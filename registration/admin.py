from django.contrib import admin

from registration.models import RegistrationSession


@admin.register(RegistrationSession)
class RegistrationSessionAdmin(admin.ModelAdmin):
    list_display = ("person", "current_step", "base_role", "status", "updated_at")
    list_filter = ("status", "base_role", "current_step")
