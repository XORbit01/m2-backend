"""
Ensures an authenticated user has a Person (and GuestProfile if created) so they
can participate in community (create posts, comments). Guest users get a Person
+ GuestProfile on first write; they then interact the same as other users.
"""

from django.contrib.auth import get_user_model

from core.models import Person
from profiles.models import GuestProfile

User = get_user_model()


def get_or_create_community_author_person(user):
    """
    Return the Person for this user so they can author posts/comments.
    If the user has no linked Person, create one with GuestProfile (guest account).
    Returns Person or None if creation failed (e.g. email already taken by another Person).
    """
    if not user or not user.is_authenticated:
        return None
    try:
        return user.person
    except Person.DoesNotExist:
        pass
    email = getattr(user, "email", None) or getattr(user, "username", "")
    full_name = (getattr(user, "get_full_name", None) or (lambda: ""))()
    if not full_name or not full_name.strip():
        full_name = email or str(user)
    if Person.objects.filter(email=email).exists():
        return None
    person = Person.objects.create(
        full_name=full_name.strip() or email,
        email=email,
        user=user,
    )
    GuestProfile.objects.create(person=person)
    return person
