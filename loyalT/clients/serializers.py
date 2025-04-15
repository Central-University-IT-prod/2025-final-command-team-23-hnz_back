from drf_yasg.inspectors import ReferencingSerializerInspector
from rest_framework import serializers

from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True, allow_null=False)
    first_name = serializers.CharField(required=True, allow_blank=True)

    def create(self, validated_data):
        instance, created = Client.objects.get_or_create(**validated_data)
        return instance

    class Meta:
        model = Client
        fields = ('id', 'first_name')


class SwaggerClientStatsLoyalView(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()


class SwaggerClientStatsLoyalViewResponse(serializers.Serializer):
    class ResultSerializer(serializers.Serializer):
        date = serializers.CharField()
        transactions_count = serializers.IntegerField()
        loyal = serializers.IntegerField()
        no_loyal = serializers.IntegerField()

    company_id = serializers.CharField()
    all_transactions_count = serializers.IntegerField()
    all_loyal = serializers.IntegerField()
    all_no_loyal = serializers.IntegerField()
    result = serializers.ListField(child=ResultSerializer())
