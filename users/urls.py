from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FreelancerProfileViewSet, CustomerProfileViewSet

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('freelancer-profiles', FreelancerProfileViewSet, basename='freelancerprofile')
router.register('customer-profiles', CustomerProfileViewSet, basename='customerprofile')

urlpatterns = [
    path('', include(router.urls)),
]
