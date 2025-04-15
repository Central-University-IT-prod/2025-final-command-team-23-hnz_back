from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import mixins
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.viewsets import GenericViewSet

from cashiers.serializers import SwaggerCashierSaleSerializer
from clients.models import Client
from companies.models import Company
from companies.serializers import CompanySerializer
from rest_framework import status as rest_status
from rest_framework.response import Response
from .models import ClientLoyalty
from .serializers import ClientLoyaltySerializer, CompanyLoyaltySerializer, SwaggerCompanyJoinLoyaltyAPI


class ClientLoyaltyAPI(APIView):
    @swagger_auto_schema(
        tags=["Client"],
        operation_id="get_client_loyalty",
        operation_summary="Получить информацию о лояльности",
        operation_description="Получение информации о статусе лояльности",
        responses={
            200: openapi.Response(
                description="Успешный запрос",
                schema=SwaggerCashierSaleSerializer(many=True)),
            404: openapi.Response(
                description="Не найдено",
                examples={
                    "application/json": {"detail": "Not found."}}
            )
        }
    )
    def get(self, request, client_id):
        client = get_object_or_404(Client, id=client_id)
        company_id = request.GET.get('company_id')
        loyalties = ClientLoyalty.objects.filter(client=client, status="ACTIVE")
        if company_id:
            company = get_object_or_404(Company, id=company_id)
            loyalties = loyalties.filter(company=company).first()
            serializer = ClientLoyaltySerializer(loyalties)
            return Response(serializer.data)

        serializer = ClientLoyaltySerializer(loyalties, many=True)
        return Response(serializer.data)


class CompanyJoinLoyaltyAPI(APIView):
    @swagger_auto_schema(
        tags=["Client"],
        operation_id="list_companies_with_loyalty_status",
        operation_summary="Список всех компаний со статусом подписки",
        operation_description="Получение полного списка компаний с информацией о подписке и баллах лояльности клиента",
        responses={
            200: openapi.Response(
                description="Успешный запрос",
                schema=SwaggerCompanyJoinLoyaltyAPI(many=True)),
            404: openapi.Response(
                description="Клиент не найден",
                examples={
                    "application/json": {"detail": "Not found."}
                }
            )
        }
    )
    def get(self, request, client_id):
        client = get_object_or_404(Client, id=client_id)

        companies = Company.objects.all()

        loyalty_datas = {
            company.id: {"company": CompanySerializer(company).data} \
                        | {"loyalty":
                               {'points': 0, 'is_subscribed': False}
                           } for company in companies
        }
        client_loyalty_companies = ClientLoyalty.objects.filter(client=client)

        for client_loyalty in client_loyalty_companies:
            loyalty_datas[client_loyalty.company.id].update({"loyalty_id": client_loyalty.id})
            loyalty_datas[client_loyalty.company.id]["loyalty"]["points"] = client_loyalty.points
            loyalty_datas[client_loyalty.company.id]["loyalty"]["is_subscribed"] = client_loyalty.status == 'ACTIVE'

        response = list(loyalty_datas.values())
        return Response(response, status=rest_status.HTTP_200_OK)


class SubscribeToCompanyAPI(APIView):
    @swagger_auto_schema(
        tags=["Client"],
        operation_id="subscribe_to_company",
        operation_summary="Подписка на компанию",
        operation_description="Активация программы лояльности клиента для указанной компании",
        responses={
            201: openapi.Response(
                description="Успешная подписка",
                examples={
                    "application/json": {"detail": "Вы успешно подписались на компанию."}
                }
            ),
            400: openapi.Response(
                description="Ошибка подписки",
                examples={
                    "application/json": {"detail": "Вы уже подписаны на эту компанию."}
                }
            ),
            404: openapi.Response(
                description="Не найдено",
                examples={
                    "application/json": {"detail": "Not found."}
                }
            )
        }
    )
    def post(self, request, client_id, company_id, *args, **kwargs):
        client = get_object_or_404(Client, id=client_id)
        company = get_object_or_404(Company, id=company_id)

        client_loyalty = ClientLoyalty.objects.filter(client=client, company=company)
        if client_loyalty.exists() and client_loyalty.first().status == 'ACTIVE':
            return Response(
                {'detail': 'Вы уже подписаны на эту компанию.'},
                status=rest_status.HTTP_400_BAD_REQUEST
            )

        ClientLoyalty.objects.update_or_create(
            client=client,
            company=company,
            defaults={'status': 'ACTIVE'}
        )

        return Response(
            {'detail': 'Вы успешно подписались на компанию.'},
            status=rest_status.HTTP_201_CREATED
        )


class UnsubscribeFromCompanyAPI(APIView):
    @swagger_auto_schema(
        tags=["Client"],
        operation_id="unsubscribe_from_company",
        operation_summary="Отписка от компании",
        operation_description="Деактивация программы лояльности клиента для указанной компании",
        responses={
            200: openapi.Response(
                description="Успешная отписка",
                examples={
                    "application/json": {"detail": "Вы успешно отписались от компании."}
                }
            ),
            400: openapi.Response(
                description="Ошибка отписки",
                examples={
                    "application/json": {"detail": "Вы не подписаны на эту компанию."}
                }
            ),
            404: openapi.Response(
                description="Не найдено",
                examples={
                    "application/json": {"detail": "Not found."}
                }
            )
        }
    )
    def delete(self, request, client_id, company_id, *args, **kwargs):
        client = get_object_or_404(Client, id=client_id)
        company = get_object_or_404(Company, id=company_id)

        try:
            client_loyalty = ClientLoyalty.objects.get(client=client, company=company)
            if client_loyalty.status == 'INACTIVE':
                return Response(
                    {'detail': 'Вы не подписаны на эту компанию.'},
                    status=rest_status.HTTP_400_BAD_REQUEST
                )
        except ClientLoyalty.DoesNotExist:
            return Response(
                {'detail': 'Вы не подписаны на эту компанию.'},
                status=rest_status.HTTP_400_BAD_REQUEST
            )

        client_loyalty.status = 'INACTIVE'
        client_loyalty.save()

        return Response(
            {'detail': 'Вы успешно отписались от компании.'},
            status=rest_status.HTTP_200_OK
        )


class ClientLoyaltyViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    alowed_methods = ('get')
    serializer_class = ClientLoyaltySerializer

    queryset = ClientLoyalty.objects.all()

    @swagger_auto_schema(
        tags=["Client"],
        operation_id="get_client_loyalty",
        operation_summary="Получить информацию о лояльности клиента",
        operation_description="Получение информации о статусе лояльности клиента для компаний",
        responses={
            200: serializer_class,
            404: openapi.Response(
                description="Не найдено",
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
