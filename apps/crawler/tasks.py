from celery import shared_task
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from django.utils import timezone
from .models import CrawlerSource, CrawlerLog
from .spiders.generic_spider import GenericSpider
from .utils import save_external_order
import logging

logger = logging.getLogger(__name__)

@shared_task
def run_crawler_for_source(source_id):
    source = CrawlerSource.objects.get(id=source_id)
    if source.status != 'active':
        logger.info(f"Source {source.name} is not active, skipping")
        return

    log = CrawlerLog.objects.create(source=source, started_at=timezone.now())
    try:
        process = CrawlerProcess(settings=get_project_settings())
        # Передаём конфиг и id источника в spider
        process.crawl(GenericSpider, source_config={
            'base_url': source.base_url,
            'crawl_config': source.crawl_config
        }, source_id=source.id)
        process.start()

        # После завершения паука нужно собрать результаты.
        # Здесь упрощённо: в реальности spider должен сохранять найденные заказы в БД через pipeline.
        # Для демонстрации вызовем save_external_order внутри паука или через сигнал.
        # В этом примере мы предполагаем, что spider сохраняет заказы через item pipeline.
        # Поэтому просто обновим лог.
        log.status = 'success'
        log.finished_at = timezone.now()
        log.save()

        source.last_run = timezone.now()
        source.status = 'active'  # сброс ошибки, если была
        source.save()

    except Exception as e:
        log.status = 'error'
        log.error_message = str(e)
        log.finished_at = timezone.now()
        log.save()
        source.status = 'error'
        source.save()
        logger.exception(f"Crawler failed for source {source.name}")

@shared_task
def run_all_crawlers():
    for source in CrawlerSource.objects.filter(status='active'):
        run_crawler_for_source.delay(source.id)