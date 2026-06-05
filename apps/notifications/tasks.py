from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import SavedSearch, Notification
from apps.orders.models import Order
from apps.orders.filters import OrderFilter
import django_filters
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_email_notification(user_email, subject, message):
    """Отправка email-уведомления"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Failed to send email to {user_email}: {e}")

@shared_task
def check_saved_searches():
    """Периодическая проверка сохранённых поисков на новые заказы"""
    now = timezone.now()
    for saved in SavedSearch.objects.all():
        # Берём фильтры из сохранённого поиска
        filters_data = saved.filters
        # Базовый queryset: опубликованные заказы, созданные после last_notified_at
        qs = Order.objects.filter(status='published')
        if saved.last_notified_at:
            qs = qs.filter(created_at__gt=saved.last_notified_at)
        else:
            qs = qs.filter(created_at__gt=timezone.datetime(2000, 1, 1, tzinfo=timezone.utc))

        # Применяем фильтры с помощью django-filters
        filter_set = OrderFilter(data=filters_data, queryset=qs)
        new_orders = filter_set.qs

        count = new_orders.count()
        if count > 0:
            # Создаём одно уведомление на все новые заказы
            Notification.objects.create(
                user=saved.freelancer,
                title=f"Новые заказы по вашему поиску «{saved.name}»",
                message=f"Найдено {count} новых заказов, соответствующих вашему сохранённому поиску.",
                notification_type='in_app'
            )
            # Обновляем дату уведомления
            saved.last_notified_at = now
            saved.save()
            logger.info(f"Notified {saved.freelancer.username} about {count} new orders for search '{saved.name}'")