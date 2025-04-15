from django.urls import path

from .views import CashierTokenObtainSlidingView, CashierLogoutAPIView, CashierPreSaleAPI
from .views import CashierSell

urlpatterns = [
    path('login/', CashierTokenObtainSlidingView.as_view(), name='cashier-login'),
    path('logout/', CashierLogoutAPIView.as_view(), name='cashier-logout'),
    path('pre-sale/', CashierPreSaleAPI.as_view(), name='cashier-pre-sale'),
    path('sell/', CashierSell.as_view(), name='cashier-sell')
]
