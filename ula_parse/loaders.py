from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst


class AutoUlaLoader(ItemLoader):
    default_item_class = dict
    title_out = TakeFirst()
    price_out = TakeFirst()
    description_out = TakeFirst()
    seller_out = TakeFirst()
