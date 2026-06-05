from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CategoryViewSet

router = DefaultRouter()
router.register('orders', OrderViewSet)
router.register('categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]