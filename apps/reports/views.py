from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Q
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime
import pandas as pd
from io import BytesIO

from apps.orders.models import Order
from apps.responses.models import Response
from apps.crawler.models import ExternalOrder, CrawlerLog, CrawlerSource

class DashboardStatsView(APIView):
    """Сводная таблица с ключевыми метриками"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Параметры периода
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        now = timezone.now()
        try:
            if start_date:
                start_date = datetime.fromisoformat(start_date)
            else:
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if end_date:
                end_date = datetime.fromisoformat(end_date)
            else:
                end_date = now
        except ValueError:
            return Response({'error': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}, status=400)

        # Агрегации
        stats = {
            'published_orders': Order.objects.filter(
                status='published', published_at__range=(start_date, end_date)
            ).count(),
            'moderation_orders': Order.objects.filter(
                status='moderation', created_at__range=(start_date, end_date)
            ).count(),
            'in_work_orders': Order.objects.filter(
                status='in_work', updated_at__range=(start_date, end_date)
            ).count(),
            'completed_orders': Order.objects.filter(
                status='completed', updated_at__range=(start_date, end_date)
            ).count(),
            'total_responses': Response.objects.filter(
                sent_at__range=(start_date, end_date)
            ).count(),
            'external_orders_found': ExternalOrder.objects.filter(
                last_seen__range=(start_date, end_date)
            ).count(),
            'crawler_errors': CrawlerLog.objects.filter(
                status='error', started_at__range=(start_date, end_date)
            ).count(),
            'active_sources': CrawlerSource.objects.filter(status='active').count(),
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
        }

        # Популярные категории (топ-5)
        popular_categories = (
            Order.objects.filter(created_at__range=(start_date, end_date))
            .values('category__name')
            .annotate(total=Count('id'))
            .order_by('-total')[:5]
        )
        stats['popular_categories'] = list(popular_categories)

        return Response(stats)


class ReportExportView(APIView):
    """Экспорт отчёта в CSV или XLSX за указанный период"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        format_type = request.query_params.get('format', 'csv').lower()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Валидация дат
        try:
            if start_date:
                start_date = datetime.fromisoformat(start_date)
            else:
                start_date = timezone.now().replace(day=1)
            if end_date:
                end_date = datetime.fromisoformat(end_date)
            else:
                end_date = timezone.now()
        except ValueError:
            return Response({'error': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}, status=400)

        if format_type not in ['csv', 'xlsx']:
            return Response({'error': 'Format must be csv or xlsx'}, status=400)

        # Данные для отчёта: список заказов за период
        orders_qs = Order.objects.filter(created_at__range=(start_date, end_date)).select_related('customer')
        data = []
        for order in orders_qs:
            data.append({
                'ID заказа': order.id,
                'Название': order.title,
                'Статус': order.get_status_display(),
                'Источник': order.get_source_display(),
                'Бюджет от': order.budget_min,
                'Бюджет до': order.budget_max,
                'Тип оплаты': order.payment_type,
                'Дедлайн': order.deadline,
                'Заказчик': order.customer.username,
                'Создан': order.created_at,
                'Опубликован': order.published_at,
            })

        df = pd.DataFrame(data)

        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="report_{start_date.date()}_{end_date.date()}.csv"'
            df.to_csv(response, index=False, encoding='utf-8-sig')
            return response

        elif format_type == 'xlsx':
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Orders')
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="report_{start_date.date()}_{end_date.date()}.xlsx"'
            return response