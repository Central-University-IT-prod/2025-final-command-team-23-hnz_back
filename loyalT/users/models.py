import uuid
from enum import Enum

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin


class User(AbstractBaseUser, PermissionsMixin):
    class UserTypeChoices(Enum):
        Company = 'Company'
        Cashier = 'Cashier'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    objects = UserManager()

    USERNAME_FIELD = "id"
    REQUIRED_FIELDS = ()

    @property
    def username(self):
        if hasattr(self, "company"):
            return self.company.username
        if hasattr(self, "cashier"):
            return self.cashier.username

    @property
    def password(self):
        if hasattr(self, "company"):
            return self.company.password
        if hasattr(self, "cashier"):
            return self.cashier.password

    class Meta:
        abstract = False
