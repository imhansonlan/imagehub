# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ImagehubItem(scrapy.Item):
    image_urls = scrapy.Field()
    images = scrapy.Field()


class LinkhubItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()


class ArticleItem(scrapy.Item):
    title = scrapy.Field()
    desc = scrapy.Field()
    extra = scrapy.Field()
