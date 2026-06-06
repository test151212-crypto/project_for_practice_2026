from django.db import models
from apps.orders.models import Order

class CrawlerSource(models.Model):
    STATUS_CHOICES = (
        ('active', 'Активен'),
        ('disabled', 'Отключён'),
        ('error', 'Ошибка'),
    )
    name = models.CharField(max_length=100)
    base_url = models.URLField()
    crawl_config = models.JSONField(help_text='Правила извлечения: {"list_selector": "...", "item_selector": "...", "fields": {"title": "css", ...}, "next_page_selector": "..."}')
    schedule = models.CharField(max_length=100, help_text='Cron строка (например, "0 * * * *")', default='0 * * * *')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_run = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ExternalOrder(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('actual', 'Актуальный'),
        ('archived', 'Архивный'),
        ('error', 'Ошибка обработки'),
    )
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='external_meta')
    source = models.ForeignKey(CrawlerSource, on_delete=models.CASCADE)
    external_id = models.CharField(max_length=200, blank=True)
    last_seen = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    suspicious = models.BooleanField(default=False)
    moderation_note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.order.title} ({self.source.name})"

class CrawlerLog(models.Model):
    source = models.ForeignKey(CrawlerSource, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20)  # success, error
    orders_found = models.IntegerField(default=0)
    orders_updated = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.source.name} - {self.started_at}"