# -*- coding: utf-8 -*-
import scrapy
import re
import json
import datetime

from xinlangweibo.items import XinlangweiboItem, CommentItem


class XinlangweiboSpiderSpider(scrapy.Spider):
    name = 'xinlangweibo_spider'

    search_name = '海清'

    def start_requests(self):
        url = f'https://s.weibo.com/user?q={self.search_name}&Refer=weibo_user'
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Host": "s.weibo.com",
            "Referer": "https://weibo.com/",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36",
        }
        yield scrapy.Request(url, headers=headers)

    def parse(self, response):
        href = response.xpath('//*[@id="pl_user_feedList"]/div[1]/div[1]/a/@href').get()
        uid = re.search('(\d+)', href).group()
        page = 1
        url = f'https://m.weibo.cn/api/container/getIndex?is_search[]=0&is_search[]=0&visible[]=0&visible[]=0&is_all[]=1&is_all[]=1&is_tag[]=0&is_tag[]=0&profile_ftype[]=1&profile_ftype[]=1&sudaref[]=passport.weibo.com&sudaref[]=passport.weibo.com&sudaref[]=passport.weibo.com&sudaref[]=passport.weibo.com&reason[]=&reason[]=&retcode[]=&retcode[]=&jumpfrom=weibocom&type=uid&value={uid}&containerid=1076031662055430'
        headers = {
            "Accept": "application/json, text/plain, */*",
            "MWeibo-Pwa": "1",
            "Referer": "https://m.weibo.cn/u/1662055430?is_search=0&is_search=0&visible=0&visible=0&is_all=1&is_all=1&is_tag=0&is_tag=0&profile_ftype=1&profile_ftype=1&page=1&page=1&sudaref=passport.weibo.com&sudaref=passport.weibo.com&sudaref=passport.weibo.com&sudaref=passport.weibo.com&reason=&reason=&retcode=&retcode=&jumpfrom=weibocom",
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Mobile Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "X-XSRF-TOKEN": "6c74a9",
        }
        yield scrapy.Request(url, headers=headers, callback=self.detail, meta={'uid': uid, 'page': page})

    def detail(self, response):
        uid = response.meta['uid']
        page = response.meta['page']
        spider_time = datetime.datetime.now().strftime('%Y-%M-%D %H:%m:%S')
        json_data = json.loads(response.text)
        data = json_data['data']
        ok = json_data['ok']
        if ok == 0:
            return
        total = data['cardlistInfo']['total']
        containerid = data['cardlistInfo']['containerid']

        cards = data['cards']
        for card in cards:
            card_type = card['card_type']
            if card_type == 9:
                blog_mid = card['mblog']['mid']  # 博文id
                attitudes_count = card['mblog']['attitudes_count']  # 点赞数
                comments_count = card['mblog']['comments_count']  # 评论数
                created_at = card['mblog']['created_at']  # 发博日期
                reposts_count = card['mblog']['reposts_count']  # 转发数
                if 'raw_text' in card['mblog']:
                    raw_text = card['mblog']['raw_text']  # 博文内容
                elif 'text' in card['mblog']:
                    raw_text = card['mblog']['text']  # 博文内容
                else:
                    raw_text = ''
                raw_text = re.sub('<.+?alt=(\[.*?\]).+?>', r'\1', raw_text)  # 先提取表情
                raw_text = re.sub('<.+?>', '', raw_text)  # 去除标签信息
                user = card['mblog']['user']
                avatar_hd = user['avatar_hd']  # 头像图片链接
                follow_count = user['follow_count']  # 他的关注数
                followers_count = user['followers_count']  # 他的粉丝数
                screen_name = user['screen_name']  # 用户名
                verified_reason = user['verified_reason']  # 微博认证

                item = XinlangweiboItem()
                item['uid'] = uid
                item['total'] = total
                item['screen_name'] = screen_name
                item['avatar_hd'] = avatar_hd
                item['follow_count'] = follow_count
                item['followers_count'] = followers_count
                item['verified_reason'] = verified_reason
                item['raw_text'] = raw_text
                item['blog_mid'] = blog_mid
                item['created_at'] = created_at
                item['attitudes_count'] = attitudes_count
                item['comments_count'] = comments_count
                item['reposts_count'] = reposts_count
                item['spider_time'] = spider_time
                yield item

                # 获取博文的回复信息
                url = f'https://m.weibo.cn/comments/hotflow?id={blog_mid}&mid={blog_mid}&max_id_type=0'

                headers = {
                    "Accept": "application/json, text/plain, */*",
                    "MWeibo-Pwa": "1",
                    "Referer": f"https://m.weibo.cn/detail/{blog_mid}",
                    "Sec-Fetch-Mode": "cors",
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1",
                    "X-Requested-With": "XMLHttpRequest",
                    "X-XSRF-TOKEN": "6c74a9",
                }
                yield scrapy.Request(url, headers=headers, callback=self.blog_comm,
                                     meta={'mid': blog_mid})

        # 翻页
        page += 1
        url = f'https://m.weibo.cn/api/container/getIndex?is_search[]=0&is_search[]=0&visible[]=0&visible[]=0&is_all[]=1&is_all[]=1&is_tag[]=0&is_tag[]=0&profile_ftype[]=1&profile_ftype[]=1&sudaref[]=passport.weibo.com&sudaref[]=passport.weibo.com&sudaref[]=passport.weibo.com&sudaref[]=passport.weibo.com&reason[]=&reason[]=&retcode[]=&retcode[]=&jumpfrom=weibocom&type=uid&value={uid}&containerid={containerid}&page={page}'
        headers = {
            "Accept": "application/json, text/plain, */*",
            "MWeibo-Pwa": "1",
            "Referer": "https://m.weibo.cn/u/1662055430?is_search=0&is_search=0&visible=0&visible=0&is_all=1&is_all=1&is_tag=0&is_tag=0&profile_ftype=1&profile_ftype=1&page=1&page=1&sudaref=passport.weibo.com&sudaref=passport.weibo.com&sudaref=passport.weibo.com&sudaref=passport.weibo.com&reason=&reason=&retcode=&retcode=&jumpfrom=weibocom",
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Mobile Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "X-XSRF-TOKEN": "c6ffe8",
        }
        yield scrapy.Request(url, headers=headers, callback=self.detail, meta={'uid': uid, 'page': page})

    def blog_comm(self, response):
        mid = response.meta['mid']
        json_data = json.loads(response.text)
        ok = json_data['ok']
        if ok != 1:
            return
        data = json_data['data']
        max_id = data['max_id']
        for comm in data['data']:
            text = comm['text']  # 评论内容
            created_at = comm['created_at']  # 评论时间
            like_count = comm['like_count']  # 评论被点赞数
            reply_count = comm['total_number']  # 评论被回复数

            uid = comm['user']['id']  # 评论人用户id
            screen_name = comm['user']['screen_name']  # 评论人名称
            avatar_hd = comm['user']['avatar_hd']  # 评论人头像
            follow_count = comm['user']['follow_count']  # 评论人关注人数
            followers_count = comm['user']['followers_count']  # 评论人被关注人数
            verified_reason = comm['user']['verified_reason']  # 认证信息

            item = CommentItem()
            item['mid'] = mid
            item['text'] = text
            item['created_at'] = created_at
            item['like_count'] = like_count
            item['reply_count'] = reply_count
            item['uid'] = uid
            item['screen_name'] = screen_name
            item['avatar_hd'] = avatar_hd
            item['follow_count'] = follow_count
            item['followers_count'] = followers_count
            item['verified_reason'] = verified_reason

            comments = comm['comments']
            if not comments:
                item['reply_text'] = ''
                item['reply_created_at'] = ''
                item['reply_uid'] = ''
                item['reply_screen_name'] = ''
                item['reply_avatar_hd'] = ''
                item['reply_follow_count'] = ''
                item['reply_followers_count'] = ''
                item['reply_verified_reason'] = ''
                yield item

            for reply in comments:
                item['reply_text'] = reply['text']
                item['reply_created_at'] = reply['created_at']
                item['reply_uid'] = reply['id']
                item['reply_screen_name'] = reply['user']['screen_name']
                item['reply_avatar_hd'] = reply['user']['avatar_hd']
                item['reply_follow_count'] = reply['user']['follow_count']
                item['reply_followers_count'] = reply['user']['followers_count']
                item['reply_verified_reason'] = reply['user']['verified_reason']
                yield item

        # 评论翻页
        url = f'https://m.weibo.cn/comments/hotflow?id={max_id}&mid={max_id}&max_id_type=0'

        headers = {
            "Accept": "application/json, text/plain, */*",
            "MWeibo-Pwa": "1",
            "Referer": f"https://m.weibo.cn/detail/{max_id}",
            "Sec-Fetch-Mode": "cors",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1",
            "X-Requested-With": "XMLHttpRequest",
            "X-XSRF-TOKEN": "6c74a9",
        }
        yield scrapy.Request(url, headers=headers, callback=self.blog_comm,
                             meta={'mid': max_id})
