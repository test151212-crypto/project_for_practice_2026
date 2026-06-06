from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/responses/', include('apps.responses.urls')),
    path('api/crawler/', include('apps.crawler.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('', TemplateView.as_view(template_name='index.html')),
]