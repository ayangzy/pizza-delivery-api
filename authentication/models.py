from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext as _
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a new user"""
        if not email:
            ValueError("User must enter an email adddress")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    
    def create_superuser(self, email, password):
        """Create a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user
    
    

class User(AbstractUser,PermissionsMixin):
    username=models.CharField(_('Username'), max_length=40,unique=True)
    email=models.CharField(_('Email'), max_length=80,unique=True)
    phone_number=PhoneNumberField(unique=True,null=False,blank=False)
    date_joined=models.DateTimeField(_('Date'),auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    #objects = UserManager()
    
    REQUIRED_FIELDS=['username','phone_number']
    USERNAME_FIELD='email'
    
    

    def __str__(self):
        return self.username