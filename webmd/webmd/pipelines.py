# -*- coding: utf-8 -*-
# scrapy web scraping project
# WEBMD pain medications

# Define item pipelines here
from scrapy.exceptions import DropItem
from scrapy.exporters import CsvItemExporter

class WebmdPipeline(object):
    # create csv file
    def __init__(self):
        self.filename = 'webmd.csv'

    def open_spider(self, spider):
        self.csvfile = open(self.filename, 'wb')
        self.exporter = CsvItemExporter(self.csvfile)
        self.exporter.fields_to_export = ['drug', 'date', 'condition', 'age', 'gender', 'treatment_length', 'reviewer_status', 'effectiveness', 'ease_of_use', 'satisfaction', 'comment']
        self.exporter.start_exporting()

    def close_spider(self, exporter):
        self.exporter.finish_exporting()
        self.csvfile.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
