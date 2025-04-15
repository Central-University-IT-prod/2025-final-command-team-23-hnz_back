from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDate
from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import GenericAPIView
from drf_yasg.utils import swagger_auto_schema  # Импорт декоратора
from rest_framework.response import Response
from rest_framework.views import APIView

from clients.models import Client
from clients.serializers import ClientSerializer, SwaggerClientStatsLoyalView, SwaggerClientStatsLoyalViewResponse
from transactions.models import Transaction


class ClientAPI(CreateModelMixin, GenericAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    @swagger_auto_schema(
        tags=["Client"],
        operation_summary="Создание клиента",
        operation_id="client_create",
        operation_description="Создание нового клиента",
        request_body=ClientSerializer,
        responses={
            200: ClientSerializer(),
            400: "Неверные входные данные",
        },
        examples={
            "application/json": {
                "id": 1,
                "first_name": "Иван Иванов"
            }
        }
    )
    def post(self, request, *args, **kwargs):
        response = self.create(request, *args, **kwargs)
        response.status_code = 200
        return response


class ClientStatsLoyalView(APIView):
    @swagger_auto_schema(
        tags=["Client"],
        operation_summary="Статистика по клиентам",
        operation_id="client_stats",
        operation_description="Получение статистики по клиентам",
        request_body=SwaggerClientStatsLoyalView,
        responses={
            200: SwaggerClientStatsLoyalViewResponse(),
            400: "Неверные входные данные",
        })
    def post(self, request):
        from_date = request.data.get('from_date')
        to_date = request.data.get('to_date')
        if not from_date or not to_date:
            return Response({"error": "Both from_date and to_date are required."}, status=status.HTTP_400_BAD_REQUEST)

        company_id = request.user.company.id
        transactions = Transaction.objects.filter(
            company_id=company_id,
            created_at__range=[from_date, to_date]
        ).annotate(day=TruncDate('created_at'))

        transactions_count = transactions.count()
        transactions_without_loyalty_count = transactions.filter(client_id__isnull=True).count()

        daily_stats = transactions.values('day').annotate(
            transactions_count=Count('id'),
            loyal=Count('id', filter=Q(client_id__isnull=False)),
            no_loyal=Count('id', filter=Q(client_id__isnull=True))
        ).order_by('-day')

        response = {
            str(company_id): {
                'company_id': str(company_id),
                'all_transactions_count': transactions_count,
                'all_loyal': transactions_count - transactions_without_loyalty_count,
                'all_no_loyal': transactions_without_loyalty_count,
                'result': []
            }
        }

        for stat in daily_stats:
            response[str(company_id)]['result'].append({
                'date': stat['day'],
                'transactions_count': stat['transactions_count'],
                'loyal': stat['loyal'],
                'no_loyal': stat['no_loyal']
            })

        return Response(list(response.values()), status=status.HTTP_200_OK)
