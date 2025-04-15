from django.urls import path

from .views import CompanyJoinLoyaltyAPI, SubscribeToCompanyAPI, UnsubscribeFromCompanyAPI, ClientLoyaltyAPI
urlpatterns = [
    path('', ClientLoyaltyAPI.as_view(), name='client-loyalty'),
    path('company', CompanyJoinLoyaltyAPI.as_view(), name='company-client-loyalty'),
    path('company/<uuid:company_id>/subscribe/', SubscribeToCompanyAPI.as_view(), name='subscribe-to-company-loyalty'),
    path('company/<uuid:company_id>/unsubscribe/', UnsubscribeFromCompanyAPI.as_view(),
         name='unsubscribe-from-company-loyalty'),
]
