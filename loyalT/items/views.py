from rest_framework import serializers, viewsets
from rest_framework import status, mixins, viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from items.models import Item, StatusEnum
from items.serializers import ItemSerializer


class ItemView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    # permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'patch', 'post']

    @swagger_auto_schema(
        tags=["Item"],
        operation_id="list_items",
        operation_summary="Получить список товаров",
        operation_description="""
        Получение списка всех товаров, принадлежащих указанной компании. 
        Товары возвращаются в виде списка с детальной информацией о каждом товаре, 
        включая его название, описание, статус (активный/неактивный) и другие параметры. 
        Доступ к этому endpoint разрешен только аутентифицированным пользователям. 
        Если компания с указанным ID не найдена, возвращается ошибка 404.
        """,
        manual_parameters=[
            openapi.Parameter(
                name='company_id',
                in_=openapi.IN_PATH,
                description="ID компании, для которой запрашиваются товары",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Список товаров",
                schema=ItemSerializer(many=True)
            ),
            404: openapi.Response(
                description="Товар не найден",
                examples={
                    "application/json": {"detail": "Not found."}
                }
            )
        }
    )
    def list(self, request, *args, **kwargs):
        self.permission_classes = ()
        return super(ItemView, self).list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Item"],
        operation_id="retrieve_item",
        operation_summary="Получить информацию о товаре",
        operation_description="""
        Получение детальной информации о конкретном товаре по его ID. 
        В ответе возвращаются все данные о товаре, включая его название, описание, статус, 
        дату создания и другие параметры. Доступ к этому endpoint разрешен только аутентифицированным пользователям. 
        Если товар с указанным ID не найден, возвращается ошибка 404.
        """,
        responses={
            200: openapi.Response(
                description="Информация о товаре",
                schema=ItemSerializer
            ),
            404: openapi.Response(
                description="Товар не найден"
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        self.permission_classes = ()
        return super(ItemView, self).retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Item"],
        operation_id="create_item",
        operation_summary="Создать новый товар",
        operation_description="""
        Создание нового товара для указанной компании. 
        В запросе необходимо передать данные о товаре, такие как название, описание, статус и другие параметры. 
        Компания, для которой создается товар, указывается через параметр company_id. 
        Доступ к этому endpoint разрешен только аутентифицированным пользователям. 
        Если company_id не указан или указан неверно, возвращается ошибка 400.
        """,
        request_body=ItemSerializer,
        responses={
            201: openapi.Response(
                description="Товар успешно создан",
                schema=ItemSerializer
            ),
            400: openapi.Response(
                description="Ошибка валидации",
                examples={
                    "application/json": {"detail": "Company ID is required"}
                }
            )
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        company_id = self.kwargs.get('company_id')
        if not company_id:
            raise serializers.ValidationError('Company ID is required')
        serializer.save(company_id=company_id)

    @swagger_auto_schema(
        tags=["Item"],
        operation_id="update_item",
        operation_summary="Обновить информацию о товаре",
        operation_description="""
        Частичное обновление информации о товаре. 
        В запросе можно передать только те поля, которые необходимо изменить. 
        Доступ к этому endpoint разрешен только аутентифицированным пользователям. 
        Если переданы неверные данные или товар с указанным ID не найден, возвращается ошибка 400 или 404 соответственно.
        """,
        request_body=ItemSerializer,
        responses={
            200: openapi.Response(
                description="Товар успешно обновлен",
                schema=ItemSerializer
            ),
            400: openapi.Response(
                description="Ошибка валидации",
                examples={
                    "application/json": {"detail": "Invalid data"}
                }
            ),
            404: openapi.Response(
                description="Товар не найден",
                examples={
                    "application/json": {"detail": "Not found."}
                }
            )
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super(ItemView, self).update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Item"],
        operation_id="list_items",
        operation_summary="Получить список товаров",
        operation_description="Получение списка всех товаров для указанной компании",
        responses={
            200: openapi.Response(
                description="Список товаров",
                schema=ItemSerializer(many=True)
            ),
            404: openapi.Response(
                description="Компания не найдена",
                examples={
                    "application/json": {"detail": "Not found."}
                }
            )
        }
    )
    def get_queryset(self):
        company_id = self.kwargs.get('company_id')
        return self.queryset.filter(company_id=company_id)
