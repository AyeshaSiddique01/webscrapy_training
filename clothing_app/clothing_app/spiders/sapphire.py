import copy
import json
from urllib.parse import urljoin, urlparse

import scrapy

from ..items import ItemColor, ItemSize, ProductItem


class SapphireSpider(scrapy.Spider):
    name = "sapphire"

    def start_requests(self):
        url = "https://pk.sapphireonline.pk/"
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        categories = response.css("div.t4s-col-item")

        for category in categories:
            category_list = []
            name = category.css("span.t4s-text::text").get()
            category_list.append(
                name
                if name
                else " ".join(category.css("h3.cstm-title-whats-new::text").getall())
            )
            category_relative_url = category.css("a::attr(href)").get()

            if name:
                absolute_url = urljoin(response.url, category_relative_url)
                yield scrapy.Request(
                    absolute_url,
                    callback=self.parse_subcategories,
                    meta={"category": category_list},
                )

    def parse_subcategories(self, response):
        categories = response.css("div.carousel-item")

        for category in categories:
            parent_categories_list = copy.deepcopy(response.meta["category"])
            next_cat = category.css("h4.carousel-title::text").get()

            if next_cat in response.css("h1.cstm-col-h-1::text").get():
                yield from self.parse_products(response, parent_categories_list)
            else:
                parent_categories_list.append(next_cat)
                category_relative_url = category.css("a::attr(href)").get()
                absolute_url = urljoin(response.url, category_relative_url)
                yield scrapy.Request(
                    absolute_url,
                    callback=self.parse_subcategories,
                    meta={"category": parent_categories_list},
                )

    def parse_products(self, response, parent_categories_list):
        products = response.css("div.t4s-product")

        for product in products:
            description_relative_url = product.css(
                "a.t4s-full-width-link::attr(href)"
            ).get()
            absolute_url = urljoin(response.url, description_relative_url)
            yield scrapy.Request(
                absolute_url,
                callback=self.parse_product_details,
                meta={"parent_categories_list": parent_categories_list},
            )

        next_page = response.css("div.t4s-pagination-wrapper a::attr(href)").get()

        if next_page:
            absolute_next_page_url = urljoin(response.url, next_page)
            yield scrapy.Request(
                absolute_next_page_url,
                callback=self.parse_subcategories,
                meta={"category": parent_categories_list},
            )

    def parse_product_details(self, response):
        item = ProductItem()

        image_urls = response.css(
            "div.t4s-product__media img.t4s-lz--fadeIn::attr(data-src)"
        ).getall()
        item["name"] = response.css("h1.t4s-product__title::text").get()
        item["price"] = response.css("span.money::text").getall()[1]
        item["in_stock"] = self.check_availability(response)
        item["details"] = self.get_details(response)
        item["items_size"] = self.get_sizes(response)
        item["category_names"] = response.meta["parent_categories_list"]
        item["image_url"] = [f"https:{img.split('?')[0]}" for img in image_urls]
        item["items_colors"] = []
        color_urls = response.css("a.cstm-tooltip::attr(href)").getall()
        color_names = response.css("a.cstm-tooltip span.tooltiptext::text").getall()

        if not color_urls:
            yield item
            return
        response.meta.update({"item": item, "color_urls": color_urls, "color_names": color_names})
        yield self.us_get_item_or_request(response)

    def us_get_item_or_request(self, response):
        if response.meta["color_urls"]:
            color_url = response.meta["color_urls"].pop()
            color_name = response.meta["color_names"].pop()
            response.meta["color_link"] = color_url
            response.meta["color_name"] = color_name

            if not urlparse(color_url).scheme:
                color_url = response.urljoin(color_url)
            return scrapy.Request(color_url, self.parse_color, meta=response.meta)

        item = response.meta["item"]
        return item

    def parse_color(self, response):
        image_urls = response.css(
            "div.t4s-product__media img.t4s-lz--fadeIn::attr(data-src)"
        ).getall()
        color = ItemColor(
            item_color=response.meta["color_name"],
            url=response.url,
            in_stock=self.check_availability(response),
            image_urls=[f"https:{img.split('?')[0]}" for img in image_urls],
        )
        response.meta["item"]["items_colors"].append(color)

        yield self.us_get_item_or_request(response)

    def get_sizes(self, response):
        sizes_response = response.css("script.pr_variants_json::text").get()
        sizes = json.loads(sizes_response) if sizes_response else []
        size_items = []

        for size in sizes:
            size_item = ItemSize()
            size_item["size_id"] = size.get("id")
            size_item["in_stock"] = size.get("inventory_quantity") > 0
            size_item["size_name"] = size.get("name")
            size_items.append(size_item)

        return size_items

    def get_details(self, response):
        script_data = response.css('script[type="application/ld+json"]::text').getall()[3]
        script_data = json.loads(script_data)
        description = script_data.get("description")

        return description.replace("&amp;amp;", "&") if description else ""

    def check_availability(self, response):
        stock_data = response.css(
            "div[data-product-featured]::attr(data-product-featured)"
        ).get()
        stock_data = json.loads(stock_data) if stock_data else {}

        return stock_data.get("available")
