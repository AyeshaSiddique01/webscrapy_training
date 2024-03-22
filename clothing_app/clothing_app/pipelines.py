# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import json
import sqlite3
from datetime import datetime

from itemadapter import ItemAdapter


class ClothingAppPipeline:
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)
        for field_name in adapter.field_names():
            if field_name == "price":
                value = adapter.get(field_name)
                adapter[field_name] = value.strip("Rs.")
        return item


class SaveToSqlitePipline:
    def __init__(self, spider):
        db_name = f"{spider.name}_{datetime.now()}"
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS PRODUCTS (
                NAME TEXT,
                PRICE TEXT,
                IN_STOCK INT,
                CATEGORY_NAMES TEXT,
                ITEMS_SIZE TEXT,
                ITEMS_COLORS TEXT,
                DETAILS TEXT,
                IMAGE_URL TEXT)'''
        )

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.spider)

    def process_item(self, item, spider):
        serialized_sizes = []
        for size in item["items_size"]:
            serialized_size = {
                "size_id": size["size_id"],
                "size_name": size["size_name"],
                "in_stock": size["in_stock"],
            }
            serialized_sizes.append(serialized_size)

        serialized_colors = []
        for color in item["items_colors"]:
            serialized_color = {
                "item_color": color["item_color"],
                "url": color["url"],
                "image_urls": color["image_urls"],
                "in_stock": color["in_stock"],
            }
            serialized_colors.append(serialized_color)

        self.cursor.execute(
            '''INSERT INTO PRODUCTS (name, price, in_stock, category_names, items_size, items_colors, details, image_url ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                item["name"],
                item["price"],
                item["in_stock"],
                json.dumps(item["category_names"]),
                json.dumps(serialized_sizes),
                json.dumps(serialized_colors),
                item["details"],
                json.dumps(item["image_url"]),
            ),
        )

        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()
