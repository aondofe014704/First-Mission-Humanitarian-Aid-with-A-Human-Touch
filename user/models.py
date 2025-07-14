from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

nigerian_phone_validator = RegexValidator(
    regex=r'^(\+234|0)[789][01]\d{8}$',
    message="Enter a valid Nigerian phone number starting with +234 or 0."
)

class User(AbstractUser):
    username = None
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[nigerian_phone_validator],
        unique=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self):
        return self.email
