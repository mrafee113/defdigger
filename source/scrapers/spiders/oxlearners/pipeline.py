from scrapy.spiders import Spider
from scrapy.item import Item

class Pipeline:
    def open_spider(self, spider: Spider):
        spider.pipeline = self
    
    def close_spider(self, spider: Spider):
        pass

    def process_item(self, item: Item, spider: Spider):
        print(item)
        return
    