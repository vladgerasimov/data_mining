import scrapy
import re
from urllib.parse import urljoin
import pymongo
from ..loaders import AutoUlaLoader


class AutoUlaSpider(scrapy.Spider):
    name = 'auto_ula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']
    xpath_selectors = {
        'brands': '//div[@class="ColumnItemList_container__5gTrc"]//a[@class="blackLink"]/@href',
        'pagination': "//div[contains(@class, 'Paginator_block')]/a/@href",
        'car': "//article[contains(@class, 'SerpSnippet_snippet__3O1t2')]"
               "//a[contains(@class, 'SerpSnippet_photoWrapper__3W9J4')]/@href"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()

    def _get_follow(self, response, selector_str, callback, **kwargs):
        for link in response.xpath(self.xpath_selectors[selector_str]).extract():
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(response, 'brands', self.parse_brand)

    def parse_brand(self, response):
        yield from self._get_follow(response, 'pagination', self.parse_brand)

        yield from self._get_follow(response, 'car', self.parse_car)

    def parse_car(self, response):
        loader = AutoUlaLoader(response=response)
        data = {
            'title': response.xpath("//div[contains(@class, 'AdvertCard_advertTitle')]//text()").extract_first(),
            'price': response.xpath("//div[@data-target='advert-price']//text()").extract_first().replace('\u2009', ''),
            'photos': response.xpath("//figure[contains(@class, 'PhotoGallery_photo')]//img/@src").extract(),
            'characteristics': tuple(
                zip(response.xpath("//div[contains(@class, 'AdvertSpecs_label')]/text()").extract(),
                    response.xpath("//div[contains(@class, 'AdvertSpecs_data')]//text()").extract())
            ),
            'description': response.xpath("//div[contains(@class, 'AdvertCard_descriptionInner')]"
                                          "//text()").extract_first(),
            'seller': self._get_seller(response)
        }
        for key, item in data.items():
            loader.add_value(key, item)
        yield loader.load_item()

    @staticmethod
    def _get_seller(response):
        start_url = 'https://youla.ru'
        marker = 'window.transitState = decodeURIComponent'
        for item in response.xpath('//script'):
            try:
                if marker in item.xpath('text()').extract_first():
                    re_pattern = re.compile(r'youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar')
                    result = re.findall(re_pattern, item.xpath('text()').extract_first())
                    return urljoin(start_url, f'/user/{result[0]}') if result else None
            except TypeError:
                pass
