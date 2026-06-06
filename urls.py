from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/orders/', include('apps.orders.urls')),
    path('api/responses/', include('apps.responses.urls')),
    path('api/crawler/', include('apps.crawler.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.orders.urls')),
    path('', TemplateView.as_view(template_name='index.html')),
]