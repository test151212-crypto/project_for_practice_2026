from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CrawlerSourceViewSet, CrawlerLogViewSet, run_crawler_manual

router = DefaultRouter()
router.register('sources', CrawlerSourceViewSet)
router.register('logs', CrawlerLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('run/<int:source_id>/', run_crawler_manual, name='run_crawler'),
]