from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework_simplejwt.tokens import RefreshToken
from cloudinary.models import CloudinaryField

# User Manager
from .managers import UserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        max_length=50,
        unique=True,
        blank=False,
        verbose_name=_("Email")
    )
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^@[\w.+-]+$',
                message='Username must start with @ and contain only letters, numbers, and . + - _',
                code='invalid_username'
            ),
        ]
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


class OneTimePassword(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, unique=True, blank=False, verbose_name=_("OTP"))

    def __str__(self):
        return f"{self.user.email}"


# class Profile(models.Model):
#     user = models.OneToOneField(
#         CustomUser,
#         on_delete=models.CASCADE,
#         related_name='profile'
#     )
#     first_name = models.CharField(max_length=50, blank=True)
#     last_name = models.CharField(max_length=50, blank=True)
#     bio = models.TextField(blank=True)
#     profile_picture = CloudinaryField('profile_picture', null=True, blank=True)

#     # Tech Experience Level
#     BEGINNER = 'Beginner'
#     INTERMEDIATE = 'Intermediate'
#     PROFESSIONAL = 'Professional'
#     EXPERIENCE_CHOICES = [
#         (BEGINNER, 'Beginner'),
#         (INTERMEDIATE, 'Intermediate'),
#         (PROFESSIONAL, 'Professional'),
#     ]
#     experience_level = models.CharField(
#         max_length=20,
#         choices=EXPERIENCE_CHOICES,
#         default=BEGINNER
#     )

#     # Collaboration and Job Preferences
#     open_to_collaboration = models.BooleanField(default=False)
#     open_for_work = models.BooleanField(default=False)

#     # Content Preferences
#     content_preferences = models.JSONField(default=list)

#     def __str__(self):
#         return f"Profile of {self.user.username}"


# # Signals to create and save profile
# @receiver(post_save, sender=CustomUser)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)


# @receiver(post_save, sender=CustomUser)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()
