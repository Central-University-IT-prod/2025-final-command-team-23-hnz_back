from django.contrib.auth import get_user_model
from django.db.models import Sum, F
from django.db.models.functions import TruncDate, TruncHour
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, mixins, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import SlidingToken
from rest_framework_simplejwt.views import TokenObtainSlidingView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from cashiers.serializers import CashierSerializer
from cashiers.models import Cashier
from companies.models import Company
from companies.serializers import CompanySerializer, CompanyTokenObtainSlidingSerializer, \
    SwaggerCompanySerializerResponse, SwaggerCompanyMoneyDailyStatsView, SwaggerCompanyMoneyDailyStatsViewResponse, \
    SwaggerCompanyMoneyDayHourlyStatsView, SwaggerCompanyMoneyDayHourlyStatsViewResponse, \
    SwaggerCompanyMoneyCashierDailyStatsViewResponse
from companies.permissions import IsUserCompany
from transaction_items.models import TransactionItem
from transactions.models import Transaction

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

User = get_user_model()


class CompanyView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'patch', 'post']

    @swagger_auto_schema(
        tags=["Company"],
        operation_id="retrieve_company",
        operation_summary="Получить информацию о компании",
        operation_description="Позволяет получить детальную информацию о компании текущего пользователя. "
                              "Если пользователь пытается получить информацию о компании, которой он не владеет, "
                              "ему будет отказано в доступе.",
        responses={
            200: SwaggerCompanySerializerResponse(),
            403: "Доступ запрещен",
            404: "Компания не найдена"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"detail": "Вы не можете получить информацию о компании другого пользователя"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Company"],
        operation_id="update_company",
        operation_summary="Обновить информацию о компании",
        operation_description="Позволяет частично обновить информацию о компании текущего пользователя. "
                              "Если пользователь пытается изменить данные чужой компании, доступ будет запрещен.",
        request_body=CompanySerializer,
        responses={
            200: CompanySerializer(),
            400: "Неверные данные",
            403: "Доступ запрещен"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.user != request.user:
            return Response(
                {"detail": "Вы не можете изменить информацию о компании другого пользователя"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def get_serializer_context(self):
        return {'request': self.request}

    @swagger_auto_schema(
        tags=["Company"],
        method='post',
        operation_id="company_logout",
        operation_summary="Выход из системы",
        operation_description="Позволяет компании выйти из системы, инвалидируя текущий токен аутентификации. "
                              "После выхода из системы токен становится недействительным.",
        responses={
            200: "Успешный выход",
            400: "Ошибка инвалидации токена"
        }
    )
    @action(methods=["post"], detail=False, url_path="logout", permission_classes=(IsAuthenticated, IsUserCompany))
    def logout(self, request):
        try:
            jti = request.auth['jti']
            user = request.user

            outstanding_token = OutstandingToken.objects.get(jti=jti, user=user)

            BlacklistedToken.objects.create(token=outstanding_token)

            return Response(status=status.HTTP_200_OK)

        except (IndexError, TokenError, Exception) as e:
            print(f"Error: {e}")
            return Response(
                {"detail": "Не удалось инвалидировать токен"},
                status=status.HTTP_400_BAD_REQUEST
            )


class CompanyRegisterAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = CompanySerializer

    @swagger_auto_schema(
        tags=["Company"],
        operation_summary="Регистрация новой компании",
        request_body=CompanySerializer,
        responses={
            201: openapi.Response(
                description="Успешная регистрация",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'company_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                        'token': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Неверные данные"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer: CompanySerializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        company = serializer.save()
        return Response(
            data={
                "company_id": company.id,
                "token": str(SlidingToken.for_user(company.user))
            },
            status=status.HTTP_200_OK
        )


class CompanyTokenObtainSlidingView(TokenObtainSlidingView):
    serializer_class = CompanyTokenObtainSlidingSerializer

    @swagger_auto_schema(
        tags=["Company"],
        operation_summary="Авторизация компании (получение токена)",
        request_body=CompanyTokenObtainSlidingSerializer,
        responses={
            200: openapi.Response(
                description="Успешная авторизация",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'token': openapi.Schema(type=openapi.TYPE_STRING),
                        'company_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid')
                    }
                )
            ),
            400: "Неверные данные",
            401: "Ошибка аутентификации"
        }
    )
    def post(self, request, *args, **kwargs):
        mutable_data = request.data.copy()

        mutable_data['user_type'] = User.UserTypeChoices.Company
        request._full_data = mutable_data
        request._data = mutable_data

        serializer = self.get_serializer(data=mutable_data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(
            serializer.validated_data | {
                'company_id': serializer.user.company.id
            },
            status=status.HTTP_200_OK
        )


class CompanyCashierViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Cashier.objects.all()
    serializer_class = CashierSerializer
    permission_classes = (IsAuthenticated, IsUserCompany,)

    def get_object(self):
        obj = get_object_or_404(self.queryset, id=self.kwargs.get('pk'))
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        queryset = self.queryset
        company_id = self.kwargs.get('company_id')
        if company_id is None:
            raise serializers.ValidationError(
                {'company': "'company_id' is required."},
            )
        return queryset.filter(company_id=company_id)

    def get_serializer_context(self):
        return {'request': self.request}

    @swagger_auto_schema(
        tags=["Cashier"],
        operation_summary="Создать нового кассира",
        request_body=CashierSerializer,
        responses={
            201: openapi.Response(
                description="Успешное создание",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'company_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                        'cashier_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                        'token': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Неверные данные",
            403: "Доступ запрещен"
        }
    )
    def create(self, request, *args, **kwargs):
        serializer: CashierSerializer = CashierSerializer(data=request.data, context=self.get_serializer_context())
        if not serializer.is_valid():
            return Response(
                {"detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cashier = serializer.save()
        return Response(
            data={
                "company_id": request.user.company.id,
                "cashier_id": cashier.id,
                "token": str(SlidingToken.for_user(cashier.user))
            },
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        tags=["Cashier"],
        operation_summary="Список кассиров компании",
        responses={
            200: CashierSerializer(many=True),
            403: "Доступ запрещен"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Cashier"],
        operation_summary="Информация о кассире",
        responses={
            200: CashierSerializer(),
            403: "Доступ запрещен",
            404: "Кассир не найден"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Cashier"],
        operation_summary="Деактивировать кассира",
        responses={
            204: "Успешная деактивация",
            403: "Доступ запрещен",
            404: "Кассир не найден"
        }
    )
    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.status = "INACTIVE"
        obj.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CompanyMoneyDailyStatsView(APIView):
    @swagger_auto_schema(
        tags=["Company"],
        operation_summary="Статистика по деньгам компании",
        request_body=SwaggerCompanyMoneyDailyStatsView,
        responses={
            200: SwaggerCompanyMoneyDailyStatsViewResponse(many=True),
            400: "Неверные данные",
            403: "Доступ запрещен",
            404: "Кассир не найден"
        }
    )
    def post(self, request, *args, **kwargs):
        from_date = request.data.get('from_date')
        to_date = request.data.get('to_date')

        if not from_date or not to_date:
            return Response({"error": "Both from_date and to_date are required."}, status=status.HTTP_400_BAD_REQUEST)

        transactions = Transaction.objects.filter(
            company_id=request.user.company.id,
            created_at__range=[from_date, to_date]
        ).annotate(day=TruncDate('created_at'))

        daily_stats = transactions.values('day').annotate(
            total_points_earned=Sum('points_earned'),
            total_price=Sum('price')
        ).order_by('-day')

        return Response(daily_stats, status=status.HTTP_200_OK)


class CompanyMoneyDayHourlyStatsView(APIView):
    @swagger_auto_schema(
        tags=["Company"],
        operation_summary="Статистика по деньгам компании по часам",
        request_body=SwaggerCompanyMoneyDayHourlyStatsView,
        responses={
            200: SwaggerCompanyMoneyDayHourlyStatsViewResponse(many=True),
            400: "Неверные данные",
            403: "Доступ запрещен",
            404: "Кассир не найден"
        }
    )
    def post(self, request, *args, **kwargs):
        date = request.data.get('date')
        if not date:
            return Response({"error": "Date is required."}, status=status.HTTP_400_BAD_REQUEST)
        company_id = request.user.company.id

        specified_date = timezone.datetime.strptime(date, '%Y-%m-%d')
        hours = [{"hour": specified_date.replace(hour=i, minute=0, second=0, microsecond=0, tzinfo=None),
                  "total_points_earned": 0,
                  "total_price": 0} for i in range(24)]

        transactions = Transaction.objects.filter(company_id=company_id,
                                                  created_at__date=specified_date).annotate(
            hour=TruncHour('created_at'))
        for transaction in transactions:
            transaction_hour = transaction.hour.replace(tzinfo=None)
            for hour in hours:
                hour_hour = hour["hour"].replace(tzinfo=None)
                if transaction_hour == hour_hour:
                    hour["total_points_earned"] += transaction.points_earned
                    hour["total_price"] += transaction.price

        return Response(hours, status=status.HTTP_200_OK)


class CompanyMoneyCashierDailyStatsView(APIView):
    @swagger_auto_schema(
        tags=["Company"],
        operation_summary="Статистика по деньгам компании по кассиру",
        request_body=SwaggerCompanyMoneyDailyStatsView,
        responses={
            200: SwaggerCompanyMoneyCashierDailyStatsViewResponse(many=True),
            400: "Неверные данные",
            403: "Доступ запрещен",
            404: "Кассир не найден"
        }
    )
    def post(self, request, *args, **kwargs):
        from_date = request.data.get('from_date')
        to_date = request.data.get('to_date')
        if not from_date or not to_date:
            return Response({"error": "Both from_date and to_date are required."}, status=status.HTTP_400_BAD_REQUEST)

        company_id = request.user.company.id

        transactions = Transaction.objects.filter(company_id=company_id,
                                                  created_at__range=[from_date, to_date]).annotate(
            day=TruncDate('created_at'))

        daily_stats = transactions.values('cashier_id', 'day').annotate(
            total_points_earned=Sum('points_earned'),
            total_price=Sum('price')
        ).order_by('cashier_id', '-day')

        result = {}
        for stat in daily_stats:
            cashier_name = Cashier.objects.get(id=stat['cashier_id']).user.username
            if cashier_name not in result:
                result[cashier_name] = {
                    'cashier_name': cashier_name,
                    'result': []
                }
            result[cashier_name]['result'].append({
                'date': stat['day'],
                'total_price': stat['total_price'],
                'total_points_earned': stat['total_points_earned']
            })

        return Response(list(result.values()))
