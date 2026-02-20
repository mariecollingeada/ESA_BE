# authentication/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_REPORTER = 'REPORTER'
    ROLE_TECHNICIAN = 'TECHNICIAN'
    ROLE_MANAGER = 'MANAGER'
    ROLE_ADMIN = 'ADMIN'

    ROLE_CHOICES = [
        (ROLE_REPORTER, 'Reporter'),
        (ROLE_TECHNICIAN, 'Technician'),
        (ROLE_MANAGER, 'Manager'),
        (ROLE_ADMIN, 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_REPORTER)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Ensure a Profile exists for every User.
    - On create: make a Profile with default role.
    - On update: ensure profile exists (create if missing) and save it.
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        # ensure a profile exists even if one was missing (defensive)
        profile, _ = Profile.objects.get_or_create(user=instance)
        # if you want to update timestamps or related fields, save
        profile.save()
