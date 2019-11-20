# -*- coding: utf-8 -*-
import scrapy
import re
import json
import datetime
import time
from xinlangweibo.items import XinlangweiboItem, CommentItem


class XinlangweiboSpiderSpider(scrapy.Spider):
    name = 'xinlangweibo_V2'



    def start_requests(self):
        with open('./to_crawl.csv', mode='r', encoding='utf-8') as f:
            names = f.readlines()

        for name in names:
            name = name.split(',')[0]
            name = str(name).strip()
            url = f'https://s.weibo.com/user?q={name}&Refer=weibo_user'
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
            break

    def parse(self, response):

        href = response.xpath('//*[@id="pl_user_feedList"]/div[1]/div[1]/a/@href').get()
        print(href)
        uid = re.findall('weibo\.com/u/(\d+?)', href)
        uname = re.findall('weibo\.com/(.+?)', href)
        if not uid:
            uname = uname[0]
            uid = ''
        else:
            uid = uid[0]
            uname = ''

        url = "https:" + href if 'https:' not in href else href
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Host": "weibo.com",
            "Referer": None,
            "Sec-Fetch-Mode": "navigate",
            'Cookies':'_s_tentry=www.csdn.net; Apache=8314278655628.751.1563271636868; SINAGLOBAL=8314278655628.751.1563271636868; ULV=1563271636885:1:1:1:8314278655628.751.1563271636868:; login_sid_t=b4b0caf66a4692f0f72222a7132cc736; cross_origin_proto=SSL; SSOLoginState=1567494102; SCF=AqcEI0VVhqToWmqeDhDgSip-zOPlUFc-INGvFPGBmyuXGvmvD7V3yzf3HRomozgtVVpmYUZ1gRO_3ADwXTyh6l8.; SUHB=0YhBw2j_0qTMdr; YF-V5-G0=8c4aa275e8793f05bfb8641c780e617b; Ugrow-G0=6fd5dedc9d0f894fec342d051b79679e; WBtopGlobal_register_version=307744aa77dd5677; ALF=1576031437; SUB=_2A25wzLedDeRhGeFP6VMU9SfOyz6IHXVQTtnVrDV8PUJbkNBeLRDDkW1NQSSdyDcN-NaDlcl0h58HLjKTAUoB3e1F; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWN5asc55wSc8jJ4fI68m0B5JpX5oz75NHD95QNeKzpSK-4eo5EWs4DqcjMi--NiK.Xi-2Ri--ciKnRi-zNS020e0M7e0eRe7tt; wvr=6; UOR=www.csdn.net,widget.weibo.com,www.baidu.com; UM_distinctid=16e6856fa4b162-0b90ddddeaaba9-5373e62-100200-16e6856fa4c80f; wb_view_log_7121559202=1366*7681; YF-Page-G0=580fe01acc9791e17cca20c5fa377d00|1574073057|1574073051; webim_unReadCount=%7B%22time%22%3A1574073085635%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C%22allcountNum%22%3A33%2C%22msgbox%22%3A0%7D',
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36",
            # "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1",
        }
        yield scrapy.Request(url, headers=headers, callback=self.get_info,
                             meta={'uid': uid, 'uname': uname})

    def get_info(self, response):
        uid = response.meta['uid']
        uname = response.meta['uname']
        PC_url = response.url
        print()
        result = re.findall('<script>.*?>(\d+)<.*?关注.*?>(\d+)<.*?粉丝.*?>(\d+)<.*?微博', response.text)
        print(result)

    def detail(self, response):
        uid = response.meta['uid']
        uname = response.meta['uname']
        PC_url = response.meta['PC_url']
        mobil_url = response.url
        _uid = re.findall('weibo\.com/u/(\d+?)\?', mobil_url)
        _uname = re.findall('weibo\.com/(.+?)\?', mobil_url)
        if uid == '' and _uid:
            uid = _uid[0]
        if uname == '' and _uname:
            uname = _uname[0]
