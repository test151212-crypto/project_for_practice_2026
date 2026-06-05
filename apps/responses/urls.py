from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResponseViewSet, ReviewViewSet, ComplaintViewSet

router = DefaultRouter()
router.register('responses', ResponseViewSet)
router.register('reviews', ReviewViewSet)
router.register('complaints', ComplaintViewSet)

urlpatterns = [
    path('', include(router.urls)),
]