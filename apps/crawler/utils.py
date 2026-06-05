from apps.orders.models import Order
from apps.crawler.models import ExternalOrder, CrawlerSource
from django.utils import timezone

def save_external_order(item, source):
    """
    Сохраняет или обновляет внешний заказ на основе данных, извлечённых краулером.
    item: dict с ключами external_id, title, description, budget, deadline, url
    source: объект CrawlerSource
    """
    defaults = {
        'title': item.get('title', 'Без названия'),
        'description': item.get('description', ''),
        'budget_min': item.get('budget'),
        'budget_max': item.get('budget'),
        'deadline': item.get('deadline'),
        'source': 'external',
        'external_url': item.get('url'),
        'external_source_name': source.name,
        'status': 'published',
        'customer': None,  # внешний заказ не привязан к пользователю
    }
    order, created = Order.objects.get_or_create(
        external_url=item.get('url'),
        defaults=defaults
    )
    if not created:
        # обновляем существующий
        for key, value in defaults.items():
            if value is not None:
                setattr(order, key, value)
        order.save()

    external, ext_created = ExternalOrder.objects.get_or_create(
        order=order,
        source=source,
        defaults={
            'external_id': item.get('external_id', ''),
            'status': 'new'
        }
    )
    if not ext_created:
        external.last_seen = timezone.now()
        external.status = 'actual'
        external.save()
    return order, created