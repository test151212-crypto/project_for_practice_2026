from django.contrib import admin
from .models import CrawlerSource, CrawlerLog, ExternalOrder

@admin.register(CrawlerSource)
class CrawlerSourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'base_url', 'status', 'last_run', 'schedule')
    list_filter = ('status',)
    search_fields = ('name', 'base_url')
    actions = ['run_crawler']

    def run_crawler(self, request, queryset):
        from .tasks import run_crawler_for_source
        for source in queryset:
            run_crawler_for_source.delay(source.id)
        self.message_user(request, 'Краулер запущен для выбранных источников')
    run_crawler.short_description = 'Запустить краулер для выбранных источников'

@admin.register(CrawlerLog)
class CrawlerLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'source', 'started_at', 'finished_at', 'status', 'orders_found')
    list_filter = ('status', 'started_at')
    readonly_fields = ('started_at', 'finished_at', 'status', 'orders_found', 'orders_updated', 'error_message')

@admin.register(ExternalOrder)
class ExternalOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'source', 'status', 'suspicious', 'last_seen')
    list_filter = ('status', 'suspicious', 'source')
    search_fields = ('order__title', 'external_id')