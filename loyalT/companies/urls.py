from django.urls import path
from rest_framework.routers import DefaultRouter

from companies.views import (CompanyView, CompanyTokenObtainSlidingView, CompanyRegisterAPIView, CompanyCashierViewSet, \
                             CompanyMoneyDayHourlyStatsView, CompanyMoneyDailyStatsView,
                             CompanyMoneyCashierDailyStatsView, )

router = DefaultRouter()
router.register(r'', CompanyView, basename='company')
router.register(r'(?P<company_id>[^/.]+)/cashier', CompanyCashierViewSet, basename='company-cashier')

urlpatterns = [
    path('login/', CompanyTokenObtainSlidingView.as_view(), name='user-auth-sign-in'),
    path('', CompanyRegisterAPIView.as_view(), name='user-auth-register'),
    path('stats/money/', CompanyMoneyDayHourlyStatsView.as_view(), name='company-stats'),
    path('stats/money/daily/', CompanyMoneyDailyStatsView.as_view(), name='company-stats'),
    path('stats/money/cashier/daily/', CompanyMoneyCashierDailyStatsView.as_view(), name='company-stats'),
]

urlpatterns += router.urls
