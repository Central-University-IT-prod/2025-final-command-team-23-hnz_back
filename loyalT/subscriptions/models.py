from django.db import models

from clients.models import Client
from companies.models import Company


# Create your models here.

class Subscription(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
