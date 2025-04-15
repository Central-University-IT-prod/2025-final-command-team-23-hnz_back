from django.db import models

from clients.models import Client
from companies.models import Company


# Create your models here.

class ClientLoyalty(models.Model):
    STATUS_CHOICES = (
        ("ACTIVE", "ACTIVE"),
        ("INACTIVE", "INACTIVE"),
    )

    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_loyalty')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='client_loyalty')
    points = models.BigIntegerField(default=0)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default="ACTIVE")

    class Meta:
        unique_together = ("client", "company")
