from django.urls import path, include
from rest_framework.routers import DefaultRouter

from items.views import ItemView

router = DefaultRouter()

router.register('', ItemView, basename='item')

urlpatterns = [
    path('item/', include(router.urls), name='item')
]
