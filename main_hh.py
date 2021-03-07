from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from ula_parse.spiders.headhunter import HeadhunterSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule('ula_parse.settings')
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(HeadhunterSpider)
    crawler_process.start()