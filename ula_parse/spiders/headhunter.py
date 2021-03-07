import scrapy
from urllib.parse import urljoin
from ..xpaths import xpath_selectors, vacancies_xpath, employer_xpath
from ..loaders import HhVacancyLoader, HhEmployerLoader


class HeadhunterSpider(scrapy.Spider):
    name = 'headhunter'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    def _get_follow(self, response, selector, callback, **kwargs):
        for link in response.xpath(xpath_selectors[selector]).extract():
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response):
        to_parse = {
            'pagination': self.parse,
            'vacancies': self.parse_vacancy
        }
        for xpath, callback in to_parse.items():
            yield from self._get_follow(response, xpath, callback)

    def parse_vacancy(self, response):
        url = 'https://hh.ru/'
        loader = HhVacancyLoader(response=response)
        loader.add_value('url', urljoin(url, response.url))
        for key, xpath in vacancies_xpath.items():
            loader.add_xpath(key, xpath)

        yield loader.load_item()

        print(1)

        yield from self._get_follow(response, 'employer', self.parse_employer)
        # yield data

    def parse_employer(self, response):
        # data = {
        #     'company_name': response.xpath("//span[@data-qa='company-header-title-name']/text()").extract_first(),
        #     'company_url': response.url,
        #     'operational_fields': response.xpath("//div[text()='Сферы деятельности']"
        #                                          "/following-sibling::p/text()").extract(),
        #     'description': ' '.join(response.xpath("//div[@data-qa='company-description-text']//text()").extract())
        # }
        # yield data
        loader = HhEmployerLoader(response=response)
        loader.add_value('company_url', response.url)
        for key, xpath in employer_xpath.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
        yield from self._get_follow(response, 'employer_vacancies', callback=self.parse)
