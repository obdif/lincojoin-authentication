from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _ 
from .managers import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import RegexValidator

# email:adebless@gmail.com
# username: @adebless
# password:1234567


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=50, unique=True, blank=False, verbose_name=_("Email"))
    # password = models.CharField(max_length=200)
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
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }
        
        
        
class OneTimePassword(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, unique=True, blank=False, verbose_name=_("OTP"))
    
    def __str__(self):
        return f"{self.user.email}"