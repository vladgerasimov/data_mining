# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline


class UlaParsePipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client['data_mining']

    def process_item(self, item, spider):
        self.db[spider.name].insert_one(item)
        return item


class DownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item['data'].get('media_url', []):
            yield Request(url)

    def item_completed(self, results, item, info):
        if item['data'].get('media_url'):
            item['data']['media_url'] = item['data']['media_url'][0]
        return item
