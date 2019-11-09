# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import time
from scrapy.exporters import JsonItemExporter


class XinlangweiboPipeline(object):
    def __init__(self):
        outfile = './out-xinlangweibo-%s.json' % time.strftime("%Y%m%d", time.strptime(time.ctime()))
        self.f1 = open(outfile, 'wb')
        self.exporter1 = JsonItemExporter(self.f1, indent=0, encoding="utf-8", ensure_ascii=False)
        self.exporter1.start_exporting()

    def process_item(self, item, spider):
        self.exporter1.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter1.finish_exporting()
        self.f1.close()
