from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSlidingSerializer

from utils.validators import validate_password

from .models import Company

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(min_length=2, max_length=255)
    max_sale = serializers.DecimalField(decimal_places=2, max_digits=3, default=0.5, min_value=0.0)
    bonus_points_ratio = serializers.DecimalField(decimal_places=2, max_digits=3, default=0.2, min_value=0.0)
    description = serializers.CharField(max_length=1000, allow_blank=True, required=False)
    username = serializers.CharField(min_length=2, max_length=255, required=False)
    password = serializers.CharField(write_only=True, min_length=8, max_length=127, validators=[validate_password],
                                     required=False)

    def update(self, instance, validated_data):
        if 'username' in validated_data:
            validated_data.pop('username')
        if 'password' in validated_data:
            validated_data.pop('password')
        return super().update(instance, validated_data)

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['user'] = User.objects.create()

        company = Company(**validated_data)
        company.set_password(password)
        try:
            company.save()
        except IntegrityError:
            raise serializers.ValidationError(
                {"username": "Company with this username already exists"}
            )
        return company

    class Meta:
        model = Company
        fields = ('id', 'username', 'password', 'name', 'max_sale', 'bonus_points_ratio', 'description',)


class CompanyTokenObtainSlidingSerializer(
    # InvalidateOldTokenSerializerMixin,
    TokenObtainSlidingSerializer
):
    username_field = Company.USERNAME_FIELD


class SwaggerCompanySerializerResponse(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    username = serializers.CharField(min_length=2, max_length=255, required=False)
    name = serializers.CharField(min_length=2, max_length=255)
    max_sale = serializers.DecimalField(decimal_places=2, max_digits=3, default=0.5)
    bonus_points_ratio = serializers.DecimalField(decimal_places=2, max_digits=3, default=0.2)
    description = serializers.CharField(max_length=1000, allow_blank=True, required=False)


class SwaggerCompanyMoneyDailyStatsView(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()


class SwaggerCompanyMoneyDailyStatsViewResponse(serializers.Serializer):
    day = serializers.DateField()
    total_points_earned = serializers.IntegerField()
    total_price = serializers.DecimalField(decimal_places=2, max_digits=30)


class SwaggerCompanyMoneyDayHourlyStatsView(serializers.Serializer):
    date = serializers.DateField()


class SwaggerCompanyMoneyDayHourlyStatsViewResponse(serializers.Serializer):
    hour = serializers.TimeField()
    total_points_earned = serializers.IntegerField()
    total_price = serializers.DecimalField(decimal_places=2, max_digits=8)

class ResultSerializerResponse(serializers.Serializer):
    date = serializers.DateField()
    total_price = serializers.DecimalField(decimal_places=2, max_digits=30)
    total_points_earned = serializers.IntegerField()


class SwaggerCompanyMoneyCashierDailyStatsViewResponse(serializers.Serializer):
    cashier_name = serializers.CharField(max_length=255)
    result = ResultSerializerResponse(many=True)
