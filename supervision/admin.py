from django.contrib import admin

from supervision.models import Supervision


@admin.register(Supervision)
class SupervisionAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "teacher", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("student__full_name", "student__email", "teacher__full_name", "teacher__email")

