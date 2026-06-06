import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy.item import Item, Field

class ExternalOrderItem(Item):
    external_id = Field()
    title = Field()
    description = Field()
    budget = Field()
    deadline = Field()
    url = Field()

class GenericSpider(scrapy.Spider):
    name = 'generic'

    def __init__(self, source_config, source_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = source_config
        self.source_id = source_id
        self.start_urls = [source_config['base_url']]

    def parse(self, response):
        # Извлекаем ссылки на карточки по селектору из конфига
        item_selector = self.config['crawl_config'].get('item_selector', '')
        if item_selector:
            for item_url in response.css(item_selector).xpath('@href').extract():
                yield Request(url=response.urljoin(item_url), callback=self.parse_item)

        # Пагинация
        next_selector = self.config['crawl_config'].get('next_page_selector')
        if next_selector:
            next_page = response.css(next_selector).xpath('@href').extract_first()
            if next_page:
                yield response.follow(next_page, self.parse)

    def parse_item(self, response):
        loader = ItemLoader(item=ExternalOrderItem(), response=response)
        fields_map = self.config['crawl_config'].get('fields', {})
        for field_name, selector in fields_map.items():
            # Поддержка CSS и XPath
            if selector.startswith('//'):
                loader.add_xpath(field_name, selector)
            else:
                loader.add_css(field_name, selector)
        # Добавляем URL страницы
        loader.add_value('url', response.url)
        yield loader.load_item()