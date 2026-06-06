from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import CrawlerSource, CrawlerLog
from .serializers import CrawlerSourceSerializer, CrawlerLogSerializer
from .tasks import run_crawler_for_source

class CrawlerSourceViewSet(viewsets.ModelViewSet):
    queryset = CrawlerSource.objects.all()
    serializer_class = CrawlerSourceSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class CrawlerLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CrawlerLog.objects.all().order_by('-started_at')
    serializer_class = CrawlerLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def run_crawler_manual(request, source_id):
    """Ручной запуск краулера для источника"""
    run_crawler_for_source.delay(source_id)
    return Response({'status': 'crawler started', 'source_id': source_id})