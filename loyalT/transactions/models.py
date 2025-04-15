from django.db import models

from clients.models import Client
from companies.models import Company
from cashiers.models import Cashier


# Create your models here.

class Transaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    client = models.ForeignKey(Client, related_name="transactions", on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, related_name="transactions", on_delete=models.CASCADE)
    cashier = models.ForeignKey(Cashier, related_name="transactions", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    price_with_sale = models.DecimalField(max_digits=8, decimal_places=2)
    points_used = models.BigIntegerField()
    points_earned = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
