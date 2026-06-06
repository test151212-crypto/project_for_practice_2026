from django.db import models
from simple_history.models import HistoricalRecords
from apps.users.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Черновик'),
        ('moderation', 'На модерации'),
        ('rework', 'На доработке'),
        ('published', 'Опубликован'),
        ('in_work', 'В работе'),
        ('on_review', 'На проверке'),
        ('needs_rework', 'Требует доработки'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
        ('rejected', 'Отклонён'),
    )
    SOURCE_CHOICES = (
        ('internal', 'Внутренний'),
        ('external', 'Внешний'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    skills = models.JSONField(default=list)                 # список необходимых навыков
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_type = models.CharField(max_length=20, choices=(('fixed', 'Фикс'), ('hourly', 'Почасовая')), default='fixed')
    deadline = models.DateTimeField()
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='internal')
    external_url = models.URLField(blank=True, null=True)
    external_source_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    moderator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='moderated_orders')
    rejection_reason = models.TextField(blank=True)
    files = models.JSONField(default=list)                 # [{filename, url, size}]
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.title