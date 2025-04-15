from django.urls import path

from .views import ClientAPI, ClientStatsLoyalView

urlpatterns = [
    path('register/', ClientAPI.as_view(), name='client-register'),
    path('stats/amount/', ClientStatsLoyalView.as_view(), name='client-stats-amount')
]
