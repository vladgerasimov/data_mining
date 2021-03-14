from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from ula_parse.spiders.instagram_subs import InstagramSubsSpider
import os
import dotenv

if __name__ == '__main__':
    dotenv.load_dotenv('.env')
    users = ['dragmethrough_hell', 'puntadelestee', 'serezhabespalov']
    crawler_settings = Settings()
    crawler_settings.setmodule('ula_parse.settings')
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(InstagramSubsSpider,
                          login=os.getenv('INST_LOGIN'),
                          password=os.getenv('INST_PASSWORD'),
                          users=users)
    crawler_process.start()