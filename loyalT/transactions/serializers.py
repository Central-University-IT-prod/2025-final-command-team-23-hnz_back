from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    client_id = serializers.IntegerField(source='client.id')
    company_id = serializers.IntegerField(source='company.id')
    cashier_id = serializers.IntegerField(source='cashier.id')
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    points_used = serializers.IntegerField()
    points_earned = serializers.IntegerField()
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Transaction
        fields = (
            'id', 'client_id', 'company_id', 'cashier_id', 'total_amount', 'points_used', 'points_earned',
            'created_at',)


class TransactionStatSerializer(serializers.Serializer):
    cashier_id = serializers.UUIDField(source="cashier.id")
    points_earned = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=8, decimal_places=2)
    created_at = serializers.DateTimeField()

    class Meta:
        model = Transaction
        fields = ["cashier_id", "points_earned", "price", "created_at"]
