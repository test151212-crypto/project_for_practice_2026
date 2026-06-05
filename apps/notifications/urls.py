from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, SavedSearchViewSet

router = DefaultRouter()
router.register('notifications', NotificationViewSet, basename='notification')
router.register('saved-searches', SavedSearchViewSet, basename='savedsearch')

urlpatterns = [
    path('', include(router.urls)),
]