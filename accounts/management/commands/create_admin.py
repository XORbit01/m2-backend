"""
Create first admin user. Run once for bootstrap.
Usage: python manage.py create_admin admin@example.com TempPass123
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create first admin (superuser) for bootstrap"

    def add_arguments(self, parser):
        parser.add_argument("email", type=str)
        parser.add_argument("password", type=str)

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING("Admin already exists"))
            return
        User.objects.create_superuser(username=email, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Admin created: {email}"))
