from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from client_loyalty.views import ClientLoyaltyViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="LoyalT API",
        default_version='v0.0.1',
        description="Loyalty program HELLO NEW ZEALAND PROD 2025 API"
    ),
    url="https://prod-team-23-j7mhbm13.REDACTED",
    public=True,
    permission_classes=[permissions.AllowAny],
)

router = DefaultRouter()
router.register(r'api/client/loyalty', ClientLoyaltyViewSet, basename='client_loyalty')

urlpatterns = [
                  re_path(
                      r"^api/swagger/$",
                      schema_view.with_ui("swagger", cache_timeout=0),
                      name="schema-swagger-ui",
                  ),
                  path('api/company/', include(("companies.urls", "companies"))),
                  path('api/company/<uuid:company_id>/', include(("items.urls", "items"))),
                  path('api/cashier/', include(("cashiers.urls", "cashiers"))),
                  path('api/admin/', admin.site.urls),
                  path('api/client/<int:client_id>/', include(("client_loyalty.urls", "client_loyalty"))),
                  path('api/client/', include(("clients.urls", "clients"))),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += router.urls
