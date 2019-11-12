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
    blog_mid = scrapy.Field()
    created_at = scrapy.Field()
    attitudes_count = scrapy.Field()
    comments_count = scrapy.Field()
    reposts_count = scrapy.Field()
    spider_time = scrapy.Field()


class CommentItem(scrapy.Item):
    mid = scrapy.Field()
    text = scrapy.Field()  # 评论内容
    created_at = scrapy.Field()  # 评论时间
    like_count = scrapy.Field()  # 评论被点赞数
    reply_count = scrapy.Field()  # 评论被回复数
    uid = scrapy.Field()  # 评论人用户id
    screen_name = scrapy.Field()  # 评论人名称
    avatar_hd = scrapy.Field()  # 评论人头像
    follow_count = scrapy.Field()  # 评论人关注人数
    followers_count = scrapy.Field()  # 评论人被关注人数
    verified_reason = scrapy.Field()  # 认证信息

    reply_text = scrapy.Field()
    reply_created_at = scrapy.Field()
    reply_uid = scrapy.Field()  # 评论人用户id
    reply_screen_name = scrapy.Field()  # 评论人名称
    reply_avatar_hd = scrapy.Field()  # 评论人头像
    reply_follow_count = scrapy.Field()  # 评论人关注人数
    reply_followers_count = scrapy.Field()  # 评论人被关注人数
    reply_verified_reason = scrapy.Field()  # 认证信息
    spider_time = scrapy.Field()
