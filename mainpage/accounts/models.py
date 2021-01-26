from django.db import models
from django.contrib.auth import models as auth_models
from django.contrib.auth.models import AbstractUser

from django.contrib import admin

class User(AbstractUser):
    pw_changing = models.BooleanField(default=False)

auth_models.User = User

# Create your models here.
