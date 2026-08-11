from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_profile(sender, instance, created, **kwargs):
    """
    Whenever a new User is saved (e.g. right after registration),
    make sure a matching Profile row exists. This means your existing
    registration view in the booking app doesn't need any changes —
    every user who signs up automatically gets a social profile.
    """
    if created:
        Profile.objects.get_or_create(user=instance)
    else:
        # If a Profile somehow doesn't exist yet for an older user
        # (e.g. users created before this app was installed), create it.
        Profile.objects.get_or_create(user=instance)
