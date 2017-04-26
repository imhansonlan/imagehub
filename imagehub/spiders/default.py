# -*- coding: utf-8 -*-
import os
import scrapy
from scrapy.spiders import Spider, Rule, CrawlSpider
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor as sel
from imagehub.items import LinkhubItem, ArticleItem
from imagehub.misc.log import *
from imagehub.misc.spider import CommonSpider


class ImageSpider(Spider):
    name = "image"
    storege_dir = 'c:\\Temp'

    def __init__(self, url=None, dir=None, *args, **kwargs):
        super(ImageSpider, self).__init__(*args, **kwargs)
        if url is None:
            raise ValueError('url must be required')
        self.start_urls = [url]
        self.dir = dir

    def save_image(self, response):
        img_url = response.url
        basename = os.path.basename(img_url)
        sdir = os.path.join(self.storege_dir, self.dir)
        if not os.path.isdir(sdir):
            os.mkdir(sdir)
        local_url = os.path.join(sdir, basename)
        # print '###', local_url, img_url
        if response.headers['Content-Type'].find('image/jpeg') > -1:
            with (open(local_url, 'wb+')) as f:
                f.write(response.body)

    def parse(self, response):
        sel = Selector(response)
        # for img_url in sel.css('.newest_vehicle_list .vehicle_img img[src*=jpg]::attr(src)').extract():
        #     print img_url
        #     yield scrapy.Request(img_url, callback=self.save_image, dont_filter=True)
        for img_url in sel.css('#gallery img[src*=tn_]::attr(src)').extract():
            img_url = img_url.replace('tn_', '')
            print img_url
            yield scrapy.Request(img_url, callback=self.save_image, dont_filter=True)


class DefaultSpider(Spider):
    name = "default"
    allowed_domains = ["localhost"]
    start_urls = [
        "http://localhost/wiki/function.checkdate/",
    ]

    def parse(self, response):
        sel = Selector(response)
        sites = sel.xpath('//*[@id="sidebar"]/div/ul/li')
        items = []
        for site in sites:
            item = LinkhubItem()
            item['title'] = site.xpath('a/text()').extract()
            item['link'] = site.xpath('a/@href').extract()
            items.append(item)
            info(item)
        return items


class WklkenSpider(CrawlSpider):
    name = "wklken"
    allowed_domains = ["wklken.me"]
    start_urls = [
        "http://wklken.me/",
    ]
    rules = [
        Rule(sel(allow=("[\d]{4}/[\d]{2}/[\d]{2}")), callback='parse_item'),
        Rule(sel(allow=("archives\.html")), follow=True),
    ]

    def parse_start_url(self, response):
        save_page(response.body)

    def parse_item(self, response):
        sel = Selector(response)
        sites = sel.xpath('//article[@id="article"]')
        items = []
        for site in sites:
            item = ArticleItem()
            item['title'] = site.xpath('//h1/text()').extract()
            item['desc'] = site.xpath('//section[@id="toc"]/div').extract()
            items.append(item)
        return items


class DoubanSpider(Spider):
    name = "douban"
    allowed_domains = ["douban.com"]
    start_urls = [
        "https://www.douban.com/",
    ]

    def parse(self, response):

        sel = Selector(response)
        sites = sel.xpath('//div[@class="anony-nav-links"]/ul/li')
        items = []
        for site in sites:
            item = LinkhubItem()
            item['title'] = site.xpath('a/text()').extract()
            item['link'] = site.xpath('a/@href').extract()
            items.append(item)
        # save_page(response.body)
        return items


class DoubanBookSpider(CrawlSpider):
    name = "doubanbook"
    allowed_domains = ["douban.com"]
    start_urls = [
        "https://book.douban.com/tag/",
    ]
    rules = [
        Rule(sel(allow=("/tag/[^/?]+$")), callback='parse_item'),
        # Rule(sel(allow=("/tag/[^/]+$", )), follow=True),
    ]

    def parse_start_url(self, response):
        save_page(response.body)

    def parse_item(self, response):
        # save_page(response.url + "\r\n", 'LISTS', 'a')
        sel = Selector(response)
        sites = sel.xpath('//ul[@class="subject-list"]/li')
        items = []
        for site in sites:
            item = LinkhubItem()
            # item['title'] = site.xpath('div/h2/a/text()').re(r'[^\r\n ]+')
            item['title'] = site.xpath('div/h2/a/@title').extract()
            item['link'] = site.xpath('div/h2/a/@href').extract()
            items.append(item)
        return items


class LocalSpider(CommonSpider):
    name = "local"
    allowed_domains = ["localhost"]
    start_urls = [
        "http://localhost/",
    ]
    rules = [
        # Rule(sel(allow=("/most_requested")), follow=True),
        Rule(sel(allow=("/wiki/function")), callback='parse_item'),
    ]
    add_rules = {
        '#content': {
            '#pyAll': {
                '__use': 'dump',
                '__list': True,
                'title': '.pyTitle h2::text',
                'desc': '#python'
            }
        },
        # '#sidebar': {
        #     'li': {
        #         '__use': 'dump',
        #         '__list': True,
        #         'title': 'a::text',
        #         'desc': 'a::attr(href)'
        #     }
        # },
        # '#logo': {
        #     '__use': 'dump',
        #     '__list': True,
        #     'extra': '::text'
        # }
    }

    def parse_item(self, response):
        items = self.parse_with_rules(response, self.add_rules, ArticleItem)
        return items
