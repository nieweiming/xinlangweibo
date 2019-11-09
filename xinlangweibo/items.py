# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class XinlangweiboItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    uid = scrapy.Field()
    total = scrapy.Field()
    avatar_hd = scrapy.Field()
    follow_count = scrapy.Field()
    followers_count = scrapy.Field()
    screen_name = scrapy.Field()
    verified_reason = scrapy.Field()
    raw_text = scrapy.Field()
    created_at = scrapy.Field()
    attitudes_count = scrapy.Field()
    comments_count = scrapy.Field()
    reposts_count = scrapy.Field()
    spider_time = scrapy.Field()
