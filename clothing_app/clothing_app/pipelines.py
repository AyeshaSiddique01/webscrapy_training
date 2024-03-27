# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import json
import sqlite3
from datetime import datetime


class ClothingAppPipeline:
    def process_item(self, item, spider):
        return item


class SaveToSqlitePipline:
    def __init__(self, spider):
        db_name = f"{spider.name}_{datetime.now()}"
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

        self.cursor.execute(
            '''create table if not exists ProductItem (
                url text,
                referer_url text,
                country_code text,
                base_sku  text,
                identifier text,
                title text,
                brand text,
                description_text text,
                available boolean,
                old_price_text NUMERIC,
                new_price_text NUMERIC,
                currency text,
                language_code text,
                color_name text,
                color_code text,
                category_names text,
                image_urls text,
                size_infos text,
                use_size_level_prices boolean,
                timestamp text)'''
        )

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.spider)

    def process_item(self, item, spider):
        serialized_sizes = []
        for size in item["size_infos"]:
            serialized_size = {
                "size_original_price_text": size.get("size_original_price_text") or 0,
                "size_current_price_text": size.get("size_current_price_text") or 0,
                "size_identifier": size.get("size_identifier") or "",
                "size_name": size.get("size_name") or "",
                "stock": size.get("stock") or 0,
            }
            serialized_sizes.append(serialized_size)

        self.cursor.execute(
            '''INSERT INTO ProductItem (url, referer_url, country_code, base_sku, identifier, title, brand, description_text, available, old_price_text, new_price_text, currency, language_code, color_name, color_code, category_names, image_urls, size_infos, use_size_level_prices, timestamp) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                item.get("url") or "",
                item.get("referer_url") or "",
                item.get("country_code") or "",
                item.get("base_sku") or "",
                item.get("identifier") or "",
                item.get("title") or "",
                item.get("brand") or "",
                item.get("description_text") or "",
                item.get("available") or False,
                item.get("old_price_text") or 0,
                item.get("new_price_text") or 0,
                item.get("currency") or "",
                item.get("language_code") or "",
                item.get("color_name") or "",
                item.get("color_code") or "",
                json.dumps(item.get("category_names") or ""),
                json.dumps(item.get("image_urls") or ""),
                json.dumps(serialized_sizes),
                item.get("use_size_level_prices") or False,
                item.get("timestamp") or ""
            ),
        )

        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()
