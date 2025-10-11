from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import string

def generate_unique_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class User(AbstractUser):
    email = models.EmailField(unique=True)
    unique_key = models.CharField(max_length=8, default=generate_unique_key, unique=True)

    REQUIRED_FIELDS = ['email']

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username