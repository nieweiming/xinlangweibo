# -*- coding: utf-8 -*-
import scrapy
import datetime
import pandas as pd
import copy

from xinlangweibo.items import WeiBoFans


def extract_cookies(cookie):
    """从浏览器或者request headers中拿到cookie字符串，提取为字典格式的cookies"""
    cookies = dict([l.split("=", 1) for l in cookie.split("; ")])
    return cookies


class weiboFans(scrapy.Spider):
    handle_httpstatus_list = [404, 500]
    name = 'weiboFans'

    custom_settings = {
        'ITEM_PIPELINES': {
            'xinlangweibo.pipelines.WeiBoFans2MongodbPipeline': 301,
        },
        'DOWNLOAD_DELAY': 1
    }
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')

    def start_requests(self):

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0',
            'Cookie': 'SINAGLOBAL=7189243138142.632.1503914703285; SCF=Aigm7UDJ-d35DH7_E41fMuGrvsy5Q22YnmLRmsEZ31H4LjnhAZ_4LCK5F4RTFyMdTs3hZ68RFhhhE9QxgUyJvvQ.; SUHB=0vJZl0BBHNHqK_; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WWp7NF3eYL0Lo-rHF-.QcdD; _s_tentry=finance.ifeng.com; UOR=,,finance.ifeng.com; YF-Page-G0=b003c396c5ae9fa75e3272879cbfcef2; Apache=5035654879416.522.1530691323733; ULV=1530691323796:76:2:2:5035654879416.522.1530691323733:1530606295716; YF-V5-G0=b4445e3d303e043620cf1d40fc14e97a; SUB=_2AkMsYAucf8NxqwJRmPEUymznaoh2ygjEieKaPPpHJRMxHRl-yj83qhEAtRB6B-AlchPZcSC0FZzlcn6AGODhIRFeVqrR',
            'Host': 'weibo.com',
        }

        cookies = extract_cookies(headers['Cookie'])
        df = pd.read_parquet('./weibo_fans.parquet')

        for cate in df.itertuples():

            name = cate.name
            weiBoUrl = cate.uid_url
            uid = cate.uid

            # if weiBoUrl.find('/u/') > 0:
            #     # uid = weiBoUrl.split('/')[4].split('?')[0]
            #     weiBoUrl = 'https://weibo.com/u/{}?is_hot=1'.format(uid)
            #     ref_tmp = 'https://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url=https%3A%2F%2Fweibo.com%2Fu%2F{uid}&domain=.weibo.com&ua=php-sso_sdk_client-0.6.28&_rand=1530692755.5581'
            # elif weiBoUrl.find('/p/') > 0:
            #     # uid = weiBoUrl.split('/')[4].split('?')[0]
            #     weiBoUrl = 'https://weibo.com/p/{}?is_all=1'.format(uid)
            #     ref_tmp = 'https://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url=https%3A%2F%2Fweibo.com%2Fu%2F{uid}&domain=.weibo.com&ua=php-sso_sdk_client-0.6.28&_rand=1530692755.5581'
            # else:
            #     # uid = weiBoUrl.split('/')[-1].split('?')[0]
            #     weiBoUrl = 'https://weibo.com/{}?is_all=1'.format(uid)
            #     ref_tmp = 'https://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url=https%3A%2F%2Fweibo.com%2F{uid}&domain=.weibo.com&ua=php-sso_sdk_client-0.6.28&_rand=1530692755.5581'

            ref_tmp = 'https://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url=https%3A%2F%2Fweibo.com%2Fu%2F{uid}&domain=.weibo.com&ua=php-sso_sdk_client-0.6.28&_rand=1530692755.5581'
            ref = ref_tmp.format(uid=uid)
            headers['Referer'] = ref
            item = WeiBoFans()
            if '/u/' not in weiBoUrl and '/p/' not in weiBoUrl:
                item['nick_name_url'] = weiBoUrl
                item['uid_url'] = ''
            else:
                item['nick_name_url'] = ''
                item['uid_url'] = weiBoUrl

            item['uid'] = uid
            item['name'] = name

            req = scrapy.Request(weiBoUrl, headers=headers, cookies=cookies, callback=self.parse_weibo)
            req.meta['item'] = copy.deepcopy(item)
            req.meta['headers'] = copy.deepcopy(headers)
            req.meta['cookies'] = copy.deepcopy(cookies)
            req.meta['ref'] = copy.deepcopy(ref)
            yield req

    def parse_weibo(self, response):
        item = copy.deepcopy(response.meta['item'])
        headers = copy.deepcopy(response.meta['headers'])
        cookies = copy.deepcopy(response.meta['cookies'])
        ref = copy.deepcopy(response.meta['ref'])

        text = response.text
        weiBoUrl = response.url

        if weiBoUrl == 'https://weibo.com/?is_hot=1':
            return

        if text.find(u'粉丝(') > 0:
            fansWeiBo = text.split(u'粉丝(')[-1].split(')')[0]
            item['fans'] = fansWeiBo

            item['date'] = self.date_str

            if '/u/' not in weiBoUrl and '/p/' not in weiBoUrl:
                item['nick_name_url'] = weiBoUrl
            else:
                item['uid_url'] = weiBoUrl
            yield item
        else:
            headers['Referer'] = ref

            if '/u/' not in weiBoUrl and '/p/' not in weiBoUrl:
                item['nick_name_url'] = weiBoUrl
            else:
                item['uid_url'] = weiBoUrl
            req = scrapy.Request(weiBoUrl, headers=headers, cookies=cookies, callback=self.parse_weiBo,
                                 dont_filter=True)
            req.meta['item'] = copy.deepcopy(item)
            req.meta['headers'] = copy.deepcopy(headers)
            req.meta['cookies'] = copy.deepcopy(cookies)
            req.meta['ref'] = copy.deepcopy(ref)
            yield req
