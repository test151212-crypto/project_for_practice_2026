from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResponseViewSet, ReviewViewSet, ComplaintViewSet

router = DefaultRouter()
router.register('responses', ResponseViewSet, basename='response')
router.register('reviews', ReviewViewSet, basename='review')
router.register('complaints', ComplaintViewSet, basename='complaint')

urlpatterns = [
    path('', include(router.urls)),
]
