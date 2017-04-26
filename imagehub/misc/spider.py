# -*- coding: utf-8 -*-

'''
CrawlSpider module process

plus 'parse_with_rules(self, response, rules, item_class, force_1_item=False)',
let you get the easy way to scrapy.

1. get sel.css()[0] for default, otherwise '__unique': False or '__list': True
2. parse dict with css for default, otherwise '__use':'dump' mean to dump data
'''

import re
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider
from scrapy.loader import ItemLoader
from .log import *


def extract_list(item_load, item_class):
    '''extract_list(item_load, item_class)

    decompose the value list of item from ItemLoader
    '''
    keys = item_load.keys()
    values = item_load.values()
    tv = zip(*values)
    items = []
    for vals in tv:
        item = item_class()
        for i, key in enumerate(keys):
            item[key] = vals[i]
        items.append(item)
    return items


class ItemLoaderSpider(CrawlSpider):
    ''' CrawlSpider process

    # Sample:
    # 1)'__use': 'dump' mean to collection data
    # 2)'__list': True mean to decompose the value list of item
    # 3)prefix support: 'c:' mean add_css, 'x:' mean add_xpath, 'v:' mean add_value,
    # use add_xpath for default if prefix is empty, it can be set for change via 'default_parse' attr.
    rules = {
        'c:#content': {
            'c:#pyAll': {
                '__use': 'dump',
                '__list': True,
                'title': 'c:.pyTitle h2::text',
                'desc': 'c:#python'
            }
        }
    }
    parse_with_rules(self, response, rules, item_class)
    '''
    default_parse = 'add_xpath'
    keywords = set(['__use', '__list'])

    def __parse_rule(self, srule):
        prefix = srule[0:2]
        rule = srule.replace(prefix, '')
        func_name = self.default_parse
        if prefix == 'c:':
            func_name = 'add_css'
        elif prefix == 'v:':
            func_name = 'add_value'
        elif prefix == 'x:':
            func_name = 'add_xpath'
        return func_name, rule

    def traversal(self, sel, rules, item_class):
        if '__use' in rules:
            l = ItemLoader(item=item_class(), selector=sel)
            if '__list' in rules:
                l.context['__list'] = True
            for field, srule in rules.items():
                if field in self.keywords:
                    continue
                func_name, rule = self.__parse_rule(srule)
                getattr(l, func_name)(field, rule)
            return l
        else:
            for nk, nv in rules.items():
                func_name, srule = self.__parse_rule(nk)
                func_name = func_name.replace('add_', '')
                sel = getattr(sel, func_name)(srule)
                return self.traversal(sel, nv, item_class)

    def parse_with_rules(self, response, rules, item_class):
        l = self.traversal(Selector(response), rules, item_class)
        items = l.load_item()
        if l.context.get('__list', False):
            items = extract_list(items, item_class)
        return items


class CommonSpider(CrawlSpider):
    '''
    Plus 'parse_with_rules(self, response, rules, item_class, force_1_item=False)',
    let you get the easy way to scrapy.

    # use parse_with_rules example:
    def parse_people_with_rules(self, response):
        item = self.parse_with_rules(response, self.all_css_rules, ZhihuPeopleItem)
        item['id'] = urlparse(response.url).path.split('/')[-1]
        info('Parsed '+response.url) # +' to '+str(item))
        return item

    # css rule example:
    all_css_rules = {
        '.zm-profile-header': {
            '.zm-profile-header-main': {
                '__use':'dump',
                'name':'.title-section .name::text',
                'sign':'.title-section .bio::text',
                'location':'.location.item::text',
                'business':'.business.item::text',
                'employment':'.employment.item::text',
                'position':'.position.item::text',
                'education':'.education.item::text',
                'education_extra':'.education-extra.item::text',
            },
            '.zm-profile-header-operation': {
                '__use':'dump',
                'agree':'.zm-profile-header-user-agree strong::text',
                'thanks':'.zm-profile-header-user-thanks strong::text',
            },
            '.profile-navbar': {
                '__use':'dump',
                'asks':'a[href*=asks] .num::text',
                'answers':'a[href*=answers] .num::text',
                'posts':'a[href*=posts] .num::text',
                'collections':'a[href*=collections] .num::text',
                'logs':'a[href*=logs] .num::text',
            },
        },
        '.zm-profile-side-following': {
            '__use':'dump',
            'followees':'a.item[href*=followees] strong::text',
            'followers':'a.item[href*=followers] strong::text',
        }
    }
    '''
    auto_join_text = True
    keywords = set(['__use', '__list'])

    # Extract content without any extra spaces.
    # NOTE: If content only has spaces, then it would be ignored.
    def extract_item(self, sels):
        contents = []
        for i in sels:
            content = re.sub(r'\s+', ' ', i.extract()).strip()
            if content != ' ':
                contents.append(content)
        return contents

    def extract_items(self, sel, rules, item):
        for nk, nv in rules.items():
            if nk in self.keywords:
                continue
            if nk not in item:
                item[nk] = []
            if sel.css(nv):
                # item[nk] += [i.extract() for i in sel.css(nv)]
                # Without any extra spaces:
                item[nk] += self.extract_item(sel.css(nv))
            else:
                item[nk] = []

    # 1. item是一个单独的item，所有数据都聚合到其中 *merge
    # 2. 存在item列表，所有item归入items
    def traversal(self, sel, rules, item_class, item, items):
        # print 'traversal:', sel, rules.keys()
        if item is None:
            item = item_class()
        if '__use' in rules:
            if '__list' in rules:
                unique_item = item_class()
                self.extract_items(sel, rules, unique_item)
                items.append(unique_item)
            else:
                self.extract_items(sel, rules, item)
        else:
            for nk, nv in rules.items():
                for i in sel.css(nk):
                    self.traversal(i, nv, item_class, item, items)

    def deal_text(self, sel, item, force_1_item, k, v):
        if v.endswith('::text') and self.auto_join_text:
            item[k] = ' '.join(self.extract_item(sel.css(v)))
        else:
            _items = self.extract_item(sel.css(v))
            if force_1_item:
                if len(_items) >= 1:
                    item[k] = _items[0]
                else:
                    item[k] = ''
            else:
                item[k] = _items

    def traversal_dict(self, sel, rules, item_class, item, items, force_1_item):
        item = {}
        for k, v in rules.items():
            if type(v) != dict:
                if k in self.keywords:
                    continue
                if type(v) == list:
                    continue
                self.deal_text(sel, item, force_1_item, k, v)
            else:
                item[k] = []
                for i in sel.css(k):
                    self.traversal_dict(i, v, item_class, item, item[k], force_1_item)
        items.append(item)

    def dfs(self, sel, rules, item_class, force_1_item):
        if sel is None:
            return []
        # Notice: items can pass ref like this, other can be not.
        items = []
        if item_class != dict:
            self.traversal(sel, rules, item_class, None, items)
        else:
            self.traversal_dict(sel, rules, item_class, None, items, force_1_item)

        return items

    def parse_with_rules(self, response, rules, item_class, force_1_item=False):
        return self.dfs(Selector(response), rules, item_class, force_1_item)
