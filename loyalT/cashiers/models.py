import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from companies.models import Company


class Cashier(AbstractBaseUser):
    STATUS_CHOICES = (
        ("ACTIVE", "ACTIVE"),
        ("INACTIVE", "INACTIVE"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, related_name="cashiers", on_delete=models.CASCADE)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=128)
    is_fired = models.BooleanField(default=False)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default="ACTIVE")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cashier'
    )

    objects = models.Manager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('username', 'password')

    def __str__(self):
        return self.username
