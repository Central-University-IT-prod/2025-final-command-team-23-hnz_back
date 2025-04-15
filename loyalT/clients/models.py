import uuid

from django.db import models

# Create your models here.

class Client(models.Model):
    id = models.BigIntegerField(primary_key=True, editable=False, null=False, blank=False)
    first_name = models.CharField(max_length=255, null=False)
