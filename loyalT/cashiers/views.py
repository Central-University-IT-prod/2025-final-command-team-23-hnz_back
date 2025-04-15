from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainSlidingView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from clients.models import Client
from items.models import Item
from transaction_items.models import TransactionItem
from .models import Cashier
from .serializers import CashierTokenObtainSlidingSerializer, CashierPreSaleSerializer, CashierSaleSerializer, \
    SwaggerCashierPreSaleSerializer, SwaggerCashierPreSaleSerializerResponse, \
    SwaggerCashierTokenObtainSlidingSerializer, SwaggerCashierTokenObtainSlidingSerializerResponse
from transactions.models import Transaction
from client_loyalty.models import ClientLoyalty
from django.db import transaction

User = get_user_model()


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CashierLogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    @swagger_auto_schema(
        tags=["Cashier"],
        operation_id="cashier_logout",
        operation_summary="Выход кассира из системы",
        operation_description='''Выход из системы, инвалидируя текущий JWT-токен. 
        Если токен успешно аннулирован, система отвечает 200 OK. В случае ошибки (например, если токен не найден 
        или уже инвалидирован) возвращается 400 Bad Request.''',
        responses={
            200: openapi.Response("Токен успешно инвалидирован"),
            400: openapi.Response("Ошибка при инвалидировании токена")
        }
    )
    def post(request, *args, **kwargs):
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


class CashierTokenObtainSlidingView(TokenObtainSlidingView):
    serializer_class = CashierTokenObtainSlidingSerializer

    @swagger_auto_schema(
        tags=["Cashier"],
        operation_id="cashier_get_token",
        operation_summary="Получение токена кассира",
        operation_description='''Аутентификация кассира и получения нового JWT-токена. 
        Кассир передает учетные данные, и при успешной проверке получает токен, который можно использовать 
        для последующих запросов к защищенным ресурсам. В случае неверных данных возвращается 400 Bad Request.''',
        request_body=SwaggerCashierTokenObtainSlidingSerializer,
        responses={
            200: openapi.Response(
                "Токен получен успешно",
                SwaggerCashierTokenObtainSlidingSerializerResponse,
            ),
            400: openapi.Response("Неверные данные для получения токена")
        }
    )
    def post(self, request, *args, **kwargs):
        mutable_data = request.data.copy()

        mutable_data['user_type'] = User.UserTypeChoices.Cashier
        request._full_data = mutable_data
        request._data = mutable_data

        serializer = self.get_serializer(data=mutable_data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(
            serializer.validated_data | {
                'cashier_id': serializer.user.cashier.id,
                'company_id': serializer.user.cashier.company.id
            },
            status=status.HTTP_200_OK
        )


class CashierPreSaleAPI(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Cashier"],
        operation_id="cashier_pre_sale",
        operation_summary="Обработка пред-продажной скидки",
        operation_description='''Расчет пред-продажной скидки на основе 
        бонусных баллов клиента. Входные данные включают сумму покупки и ID клиента. 
        В ответе API возвращает информацию о примененной скидке, оставшемся балансе клиента и окончательной 
        стоимости покупки.''',
        request_body=SwaggerCashierPreSaleSerializer,
        responses={
            200: openapi.Response(
                description="Скидка успешно рассчитана",
                schema=SwaggerCashierPreSaleSerializerResponse,
            ),
            400: openapi.Response("Ошибка при обработке пред-продажной скидки")
        }
    )
    def post(self, request, *args, **kwargs):
        pre_sale = CashierPreSaleSerializer(data=request.data)
        pre_sale.is_valid(raise_exception=True)

        client = get_object_or_404(Client, id=pre_sale.validated_data['client_id'])
        company = request.user.cashier.company

        client_loyalty, created = ClientLoyalty.objects.get_or_create(client=client, company=company)

        points_used = min(
            pre_sale.validated_data['total_price'] * company.max_sale, client_loyalty.points
        )

        price_with_sale = pre_sale.validated_data['total_price'] - points_used

        after_sale_balance = client_loyalty.points - points_used

        points_earn = company.bonus_points_ratio * pre_sale.validated_data['total_price']

        response = {
            "client_balance": client_loyalty.points,
            "price_with_sale": price_with_sale,
            "points_used": points_used,
            "after_sale_balance": after_sale_balance,
            'points_earn': points_earn
        }

        return Response(response, status=status.HTTP_200_OK)


class CashierSell(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Cashier"],
        operation_description="Продажа товара и начисление бонусов",
        operation_summary="Продажа товара и начисление бонусов",
        request_body=CashierSaleSerializer,
        responses={
            200: openapi.Response("Продажа успешно завершена"),
            404: openapi.Response("Клиент или товар не найден"),
            400: openapi.Response("Ошибка при оформлении продажи")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = CashierSaleSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        if not hasattr(request.user, 'cashier'):
            raise PermissionDenied()

        cashier = request.user.cashier
        company = cashier.company

        client = get_object_or_404(Client, id=data['client_id']) if data['client_id'] else None

        with transaction.atomic():
            points_earned = int(data["total_price_with_sale"] * company.bonus_points_ratio) if client else 0
            transaction_obj = Transaction.objects.create(
                client=client,
                company=company,
                cashier=cashier,
                price=data["total_price"],
                price_with_sale=data["total_price_with_sale"],
                points_used=data["points_used"],
                points_earned=points_earned,
            )
            if client:
                client_loyalty = get_object_or_404(ClientLoyalty, client_id=data['client_id'], company_id=company.id)
                if data["points_used"] == 0:
                    client_loyalty.points += points_earned
                client_loyalty.points -= data["points_used"]
                client_loyalty.save()

            item_objects = []

            for item in data["items"]:
                try:
                    item_obj = Item.objects.get(id=item["item_id"])
                except:
                    raise NotFound("Item not found")
                item_objects.append(
                    TransactionItem(
                        transaction=transaction_obj,
                        item=item_obj,
                        quantity=item["quantity"],
                        sell_price=item["sell_price"],
                        origin_price=item_obj.price,
                    )
                )

            TransactionItem.objects.bulk_create(item_objects)

        return Response(status=status.HTTP_200_OK)
