from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.models import Person

User = get_user_model()


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "user", "created_at")
    search_fields = ("full_name", "email")
    raw_id_fields = ("user",)
    autocomplete_fields = []


class PersonInline(admin.StackedInline):
    model = Person
    can_delete = False
    verbose_name_plural = "Person"
    fk_name = "user"
    raw_id_fields = ()


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (PersonInline,)
