# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UlaParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class InstagramItem(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
