# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import time
from scrapy.exporters import JsonItemExporter
from xinlangweibo.items import XinlangweiboItem, CommentItem, WeiBoFans
import datetime
import pandas as pd
import os
import pyhdfs
import logging
from pymongo import MongoClient
from utils.private import MONGODB_IP
from utils.private import MONGODB_PORT
from utils.private import MONGODB_DATABASE_NAME
from utils.private import MONGODB_TABLE_NAME
from utils.private import HDFS_IP
from utils.private import HDFS_PORT
from utils.private import HDFS_USER


class XinlangweiboPipeline(object):
    def __init__(self):
        outfile = './out-xinlangweibo-%s.json' % time.strftime("%Y%m%d", time.strptime(time.ctime()))
        self.f1 = open(outfile, 'wb')
        self.exporter1 = JsonItemExporter(self.f1, indent=0, encoding="utf-8", ensure_ascii=False)
        self.exporter1.start_exporting()

        outfile2 = './out-xinlangweibo-comment-%s.json' % time.strftime("%Y%m%d", time.strptime(time.ctime()))
        self.f2 = open(outfile2, 'wb')
        self.exporter2 = JsonItemExporter(self.f2, indent=0, encoding="utf-8", ensure_ascii=False)
        self.exporter2.start_exporting()

    def process_item(self, item, spider):
        if isinstance(item, XinlangweiboItem):
            self.exporter1.export_item(item)
        elif isinstance(item, CommentItem):
            self.exporter2.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter1.finish_exporting()
        self.f1.close()
        self.exporter2.finish_exporting()
        self.f2.close()


class WeiBoFans2LocalPipeline(object):
    def __init__(self):
        outfile = './out-weibofans-%s.json' % time.strftime("%Y%m%d", time.strptime(time.ctime()))
        self.f1 = open(outfile, 'wb')
        self.exporter1 = JsonItemExporter(self.f1, indent=0, encoding="utf-8", ensure_ascii=False)
        self.exporter1.start_exporting()

    def process_item(self, item, spider):
        self.exporter1.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter1.finish_exporting()
        self.f1.close()


class WeiBoFans2MongodbPipeline(object):
    def __init__(self):
        self.client = MongoClient(MONGODB_IP, MONGODB_PORT)
        self.db = self.client[MONGODB_DATABASE_NAME]
        self.table = self.db[MONGODB_TABLE_NAME]

        self.today = datetime.datetime.now().strftime('%Y-%m-%d')

    def process_item(self, item, spider):
        item = dict(item)
        self.table.insert_one(item)
        return item

    def close_spider(self, spider):
        cursor = self.table.find({'date': self.today}, {'_id': 0})
        data = [d for d in cursor]
        self.client.close()

        df = pd.DataFrame(data, dtype=str)
        df = df[['date', 'name', 'fans', 'uid', 'nick_name_url', 'uid_url']]

        df.drop_duplicates(inplace=True)
        parquet_file = f'weibo_fans{self.today}.parquet'
        df.to_parquet(parquet_file, compression=None)

        # 上传hive
        hdfs_client = pyhdfs.HdfsClient(HDFS_IP, HDFS_PORT, HDFS_USER)
        hdfs_path = f'/data/crawler/crawler_weibo_fans/{parquet_file}'  # hdfs文件地址
        hdfs_client.copy_from_local(parquet_file, hdfs_path, permission=755)

        # 删除本地文件
        if os.path.exists(parquet_file):
            os.remove(parquet_file)

        # 日志记录
        logging.info(parquet_file)
