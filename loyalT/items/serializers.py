from rest_framework import serializers
from .models import Item


class ItemSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    company_id = serializers.UUIDField(source='company.id', read_only=True)
    name = serializers.CharField(max_length=255)
    price = serializers.DecimalField(decimal_places=2, max_digits=10)
    status = serializers.CharField(max_length=8, default='active')
    description = serializers.CharField(max_length=255, allow_null=True, required=False)
    image = serializers.ImageField(required=False)

    class Meta:
        model = Item
        fields = ('id', 'company_id', 'name', 'price', 'status', 'description', 'image')
