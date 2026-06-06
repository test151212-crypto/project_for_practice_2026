import django_filters
from .models import Order

class OrderFilter(django_filters.FilterSet):
    # Диапазон бюджета
    budget_min = django_filters.NumberFilter(field_name='budget_min', lookup_expr='gte')
    budget_max = django_filters.NumberFilter(field_name='budget_max', lookup_expr='lte')
    # Диапазон срока выполнения
    deadline_from = django_filters.DateTimeFilter(field_name='deadline', lookup_expr='gte')
    deadline_to = django_filters.DateTimeFilter(field_name='deadline', lookup_expr='lte')
    # Диапазон даты публикации
    published_at_from = django_filters.DateTimeFilter(field_name='published_at', lookup_expr='gte')
    published_at_to = django_filters.DateTimeFilter(field_name='published_at', lookup_expr='lte')
    # Рейтинг заказчика от/до
    customer_rating_min = django_filters.NumberFilter(field_name='customer__customer_profile__rating', lookup_expr='gte')
    customer_rating_max = django_filters.NumberFilter(field_name='customer__customer_profile__rating', lookup_expr='lte')
    # Навыки (содержит строку)
    skills_contains = django_filters.CharFilter(field_name='skills', lookup_expr='contains')
    # Категория, источник, статус, тип оплаты
    category = django_filters.NumberFilter(field_name='category__id')
    source = django_filters.ChoiceFilter(choices=Order.SOURCE_CHOICES)
    status = django_filters.ChoiceFilter(choices=Order.STATUS_CHOICES)
    payment_type = django_filters.ChoiceFilter(choices=(('fixed', 'Фикс'), ('hourly', 'Почасовая')))

    class Meta:
        model = Order
        fields = ['category', 'source', 'status', 'payment_type',
                  'budget_min', 'budget_max', 'deadline_from', 'deadline_to',
                  'published_at_from', 'published_at_to',
                  'customer_rating_min', 'customer_rating_max', 'skills_contains']