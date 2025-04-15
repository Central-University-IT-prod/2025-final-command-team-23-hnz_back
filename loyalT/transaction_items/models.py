from django.db import models

from items.models import Item
from transactions.models import Transaction


# Create your models here.

class TransactionItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    sell_price = models.DecimalField(decimal_places=2, max_digits=8)
    origin_price = models.DecimalField(decimal_places=2, max_digits=8)
