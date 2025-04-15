from rest_framework import serializers
from .models import TransactionItem


class TransactionItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    transaction_id = serializers.IntegerField(source='transaction.id', read_only=True)

    class Meta:
        model = TransactionItem
        fields = ('id', 'transaction_id',)
