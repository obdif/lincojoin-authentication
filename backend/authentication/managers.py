from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _ 
from django.core.exceptions import ValidationError
from django.core.validators import validate_email



class UserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("Please Enter a valid email"))
        
    def create_user(self, email, password, **extra_fields):
        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_("An email address is required"))
        if not password:
            raise ValueError(_("Password is required"))
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user 
    
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_staff", True)
        
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Is SuperUser must be true for admin"))
        if extra_fields.get("is_verified") is not True:
            raise ValueError(_("Is Verified must be true for admin"))
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Is Staff must be true for admin"))
        
        user = self.create_user(email, password, **extra_fields)
        user.save(using=self._db)
        return user