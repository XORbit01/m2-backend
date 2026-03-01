"""
Django admin custom views for testing (e.g. create test user).
Staff-only.
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from core.models import Person

User = get_user_model()

# Default test credentials (hardcoded for testing)
DEFAULT_TEST_EMAIL = "test@example.com"
DEFAULT_TEST_PASSWORD = "testpass123"
DEFAULT_TEST_FULL_NAME = "Test User"


@staff_member_required
@require_http_methods(["GET", "POST"])
@csrf_protect
def create_test_user(request):
    """
    Create a User + Person for testing (registration flow, login, etc.).
    GET: show form with default credentials.
    POST: create user and display credentials.
    """
    if request.method == "POST":
        email = request.POST.get("email", DEFAULT_TEST_EMAIL).strip()
        password = request.POST.get("password", DEFAULT_TEST_PASSWORD)
        full_name = request.POST.get("full_name", DEFAULT_TEST_FULL_NAME).strip()

        error = None
        if not email:
            error = "Email is required."
        elif User.objects.filter(email=email).exists():
            error = f"User with email {email} already exists."
        elif Person.objects.filter(email=email).exists():
            error = f"Person with email {email} already exists."

        if error:
            return render(
                request,
                "admin/accounts/create_test_user.html",
                {
                    "error": error,
                    "email": email,
                    "full_name": full_name,
                },
            )

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
        )
        person = Person.objects.create(
            full_name=full_name,
            email=email,
            user=user,
        )

        return render(
            request,
            "admin/accounts/create_test_user.html",
            {
                "created": True,
                "email": email,
                "password": password,
                "full_name": full_name,
                "user_id": user.id,
                "person_id": person.id,
            },
        )

    return render(
        request,
        "admin/accounts/create_test_user.html",
        {
            "email": DEFAULT_TEST_EMAIL,
            "password": DEFAULT_TEST_PASSWORD,
            "full_name": DEFAULT_TEST_FULL_NAME,
        },
    )
