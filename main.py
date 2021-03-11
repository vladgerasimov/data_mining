from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from ula_parse.spiders.instagram import InstagramSpider
import os
import dotenv

if __name__ == '__main__':
    dotenv.load_dotenv('.env')
    tags = ['python', 'ufc']
    crawler_settings = Settings()
    crawler_settings.setmodule('ula_parse.settings')
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(InstagramSpider,
                          login=os.getenv('INST_LOGIN'),
                          password=os.getenv('INST_PASSWORD'),
                          tags=tags)
    crawler_process.start()