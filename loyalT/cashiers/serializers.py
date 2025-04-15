from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSlidingSerializer

from companies.models import Company
from utils.validators import validate_password
from utils.mixins import InvalidateOldTokenSerializerMixin

from .models import Cashier

User = get_user_model()


class CashierSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    company_id = serializers.UUIDField(source='company.id', read_only=True)
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8, max_length=127, validators=[validate_password])
    status = serializers.CharField(read_only=True)

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['user'] = User.objects.create()
        validated_data['company'] = self.context["request"].user.company

        cashier = Cashier(**validated_data)
        cashier.set_password(password)
        try:
            cashier.save()
        except IntegrityError:
            raise serializers.ValidationError(
                {"username": "Cashier with this username already exists"}
            )
        return cashier

    class Meta:
        model = Cashier
        fields = ('id', 'company_id', 'username', 'password', 'status',)


class CashierTokenObtainSlidingSerializer(
    # InvalidateOldTokenSerializerMixin,
    TokenObtainSlidingSerializer
):
    username_field = Cashier.USERNAME_FIELD


class CashierPreSaleSerializer(serializers.Serializer):
    client_id = serializers.IntegerField()
    total_price = serializers.DecimalField(max_digits=8, decimal_places=2)


class CashierItemSerializer(serializers.Serializer):
    item_id = serializers.UUIDField()
    quantity = serializers.IntegerField()
    sell_price = serializers.DecimalField(max_digits=8, decimal_places=2)


class CashierSaleSerializer(serializers.Serializer):
    items = serializers.ListField(child=CashierItemSerializer())
    total_price_with_sale = serializers.DecimalField(max_digits=8, decimal_places=2)
    total_price = serializers.DecimalField(max_digits=8, decimal_places=2)
    points_used = serializers.IntegerField()
    client_id = serializers.IntegerField(allow_null=True)


class SwaggerCashierTokenObtainSlidingSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class SwaggerCashierTokenObtainSlidingSerializerResponse(serializers.Serializer):
    cashier_token = serializers.CharField()
    company_id = serializers.UUIDField()
    cashier_id = serializers.UUIDField()


class SwaggerCashierPreSaleSerializer(serializers.Serializer):
    class SwaggerCashierPreSaleSerializerChild(serializers.Serializer):
        id = serializers.UUIDField()
        company_id = serializers.UUIDField()
        name = serializers.CharField()
        price = serializers.DecimalField(max_digits=8, decimal_places=2)
        status = serializers.CharField()
        description = serializers.CharField(),
        cnt = serializers.IntegerField()

    items = serializers.ListField(child=SwaggerCashierPreSaleSerializerChild())
    client_id = serializers.IntegerField(allow_null=True)
    total_price = serializers.DecimalField(max_digits=8, decimal_places=2)


class SwaggerCashierPreSaleSerializerResponse(serializers.Serializer):
    client_balance = serializers.IntegerField()
    price_with_sale = serializers.DecimalField(max_digits=8, decimal_places=2)
    points_used = serializers.IntegerField()
    after_sale_balance = serializers.IntegerField()
    points_earn = serializers.DecimalField(max_digits=8, decimal_places=2)


class SwaggerCashierSaleSerializer(serializers.Serializer):
    class SwaggerCashierSaleSerializerChild(serializers.Serializer):
        item_id = serializers.UUIDField()
        quantity = serializers.IntegerField()
        sell_price = serializers.DecimalField(max_digits=8, decimal_places=2)

    items = serializers.ListField(child=SwaggerCashierSaleSerializerChild())
    total_price_with_sale = serializers.DecimalField(max_digits=8, decimal_places=2)
    total_price = serializers.DecimalField(max_digits=8, decimal_places=2)
    points_used = serializers.IntegerField()
    client_id = serializers.IntegerField(allow_null=True)

