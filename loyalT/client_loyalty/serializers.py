from rest_framework import serializers
from .models import ClientLoyalty
from drf_yasg.utils import swagger_serializer_method

class ClientLoyaltySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    company_id = serializers.CharField(source="company.id", read_only=True)

    class Meta:
        model = ClientLoyalty
        fields = ["id", "company_id", "company_name", "points", "status"]


class CompanyLoyaltySerializer(serializers.Serializer):
    loyalty_id = serializers.IntegerField()
    company_id = serializers.CharField(source='company.id')
    company_name = serializers.CharField(source='company.name')
    username = serializers.CharField(source='company.username')
    max_sale = serializers.DecimalField(source='company.max_sale', max_digits=3, decimal_places=2)
    bonus_points_ratio = serializers.DecimalField(source='company.bonus_points_ratio', max_digits=3, decimal_places=2)
    description = serializers.CharField(source='company.description', required=False, allow_null=True, allow_blank=True)
    loyalty = serializers.SerializerMethodField()

    def get_loyalty(self, obj):
        loyalty_data = obj.get('loyalty')
        if loyalty_data:
            return {
                'points': loyalty_data['points'],
                'is_subscribed': loyalty_data['is_subscribed']
            }
        return None


class SwaggerClientLoyaltyAPI(serializers.Serializer):
    id = serializers.IntegerField()
    company_id = serializers.UUIDField()
    company_name = serializers.CharField()
    points = serializers.IntegerField()
    status = serializers.CharField()


class CompanySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    username = serializers.CharField()
    name = serializers.CharField()
    max_sale = serializers.DecimalField(max_digits=3, decimal_places=2)
    bonus_points_ratio = serializers.DecimalField(max_digits=3, decimal_places=2)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        ref_name = "ClientLoyaltyCompany"  # Уникальное имя

class LoyaltySerializer(serializers.Serializer):
    points = serializers.IntegerField()
    is_subscribed = serializers.BooleanField()

    class Meta:
        ref_name = "ClientLoyaltyLoyalty"  # Уникальное имя

class SwaggerCompanyJoinLoyaltyAPI(serializers.Serializer):
    @swagger_serializer_method(serializer_or_field=CompanySerializer())
    def get_company(self, obj):
        return CompanySerializer(obj.get("company")).data if obj.get("company") else None

    @swagger_serializer_method(serializer_or_field=LoyaltySerializer())
    def get_loyalty(self, obj):
        return LoyaltySerializer(obj.get("loyalty")).data if obj.get("loyalty") else None

    company = serializers.SerializerMethodField()
    loyalty = serializers.SerializerMethodField()
    loyalty_id = serializers.IntegerField()
