import scrapy
import re
from urllib.parse import urljoin
import pymongo


class AutoUlaSpider(scrapy.Spider):
    name = 'auto_ula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']
    css_selectors = {
        'brands': 'div.ColumnItemList_container__5gTrc a.blackLink',
        'pagination': 'div.Paginator_block__2XAPy a.Paginator_button__u1e7D',
        'car': 'article.SerpSnippet_snippet__3O1t2 div.SerpSnippet_titleWrapper__38bZM a.blackLink'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()

    def _get_follow(self, response, selector_str, callback, **kwargs):
        for a in response.css(self.css_selectors[selector_str]):
            link = a.attrib.get('href')
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(response, 'brands', self.parse_brand)

    def parse_brand(self, response, *args, **kwargs):
        yield from self._get_follow(response, 'pagination', self.parse_brand)

        yield from self._get_follow(response, 'car', self.parse_car)

    def parse_car(self, response, *args, **kwargs):
        data = {
            'title': response.css('div.AdvertCard_advertTitle__1S1Ak::text').extract_first(),
            'price': response.css('div.AdvertCard_price__3dDCr::text').extract_first().replace('\u2009', ''),
            'photos': response.css('figure.PhotoGallery_photo__36e_r picture img.'
                                   'PhotoGallery_photoImage__2mHGn::attr(src)').extract(),
            'characteristics': tuple(
                zip(response.css('div.AdvertCard_specs__2FEHc div.AdvertSpecs_label__2JHnS::text').extract(),
                    response.css('div.AdvertCard_specs__2FEHc div.AdvertSpecs_data__xK2Qx ::text').extract())
            ),
            'description': response.css('div.AdvertCard_descriptionInner__KnuRi::text').extract_first(),
            'seller': self._get_seller(response)
        }

        self.db_client['data_mining'][self.name].insert_one(data)
        print(data)

    @staticmethod
    def _get_seller(response):
        start_url = 'https://youla.ru'
        marker = 'window.transitState = decodeURIComponent'
        for item in response.css('script'):
            try:
                if marker in item.css('::text').extract_first():
                    re_pattern = re.compile(r'youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar')
                    result = re.findall(re_pattern, item.css('::text').extract_first())
                    return urljoin(start_url, f'/user/{result[0]}') if result else None
            except TypeError:
                pass
