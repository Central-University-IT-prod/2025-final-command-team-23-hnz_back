import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class Company(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=128)
    max_sale = models.DecimalField(decimal_places=2, max_digits=3, default=0.5)
    bonus_points_ratio = models.DecimalField(decimal_places=2, max_digits=3, default=0.2)
    description = models.TextField(null=True, blank=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company'
    )

    objects = models.Manager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('name', 'password')

    def __str__(self):
        return self.name