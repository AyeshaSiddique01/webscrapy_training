import copy
import json
from urllib.parse import urljoin

import scrapy

from ..items import ProductItem, SizeItem


class SapphireSpider(scrapy.Spider):
    name = "sapphire"

    def start_requests(self):
        url = "https://pk.sapphireonline.pk/"
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        categories = response.css("div.t4s-col-item")

        for category in categories:
            category_list = []
            category_name = self.get_category_name(category)
            category_list.append(category_name)
            category_relative_url = category.css("a::attr(href)").get()

            if category_name:
                absolute_url = urljoin(response.url, category_relative_url)
                yield scrapy.Request(absolute_url, callback=self.parse_subcategories,
                                     meta={"category_names": category_list},
                )
    
    def get_category_name(self, response):
        name = response.css("span.t4s-text::text").get()
        return name if name else " ".join(response.css("h3.cstm-title-whats-new::text").getall())
        

    def parse_subcategories(self, response):
        categories = response.css("div.carousel-item")

        for category in categories:
            parent_categories_list = copy.deepcopy(response.meta["category_names"])
            next_cat = category.css("h4.carousel-title::text").get()

            if next_cat in response.css("h1.cstm-col-h-1::text").get():
                yield from self.parse_products(response, parent_categories_list)
            else:
                parent_categories_list.append(next_cat)
                category_relative_url = category.css("a::attr(href)").get()
                absolute_url = urljoin(response.url, category_relative_url)
                yield scrapy.Request(absolute_url, callback=self.parse_subcategories,
                                     meta={"category_names": parent_categories_list},
                )

    def parse_products(self, response, parent_categories_list):
        for product in response.css("div.t4s-product"):
            description_relative_url = product.css("a.t4s-full-width-link::attr(href)").get()
            absolute_url = urljoin(response.url, description_relative_url)

            yield scrapy.Request(absolute_url, callback=self.parse_product_details,
                                 meta={"parent_categories_list": parent_categories_list},
            )

        next_page = response.css("div.t4s-pagination-wrapper a::attr(href)").get()

        if next_page:
            absolute_next_page_url = urljoin(response.url, next_page)
            yield scrapy.Request(absolute_next_page_url, callback=self.parse_subcategories,
                                 meta={"category_names": parent_categories_list},
            )

    def parse_product_details(self, response):
        script_data = self.get_script_data(response)

        item = ProductItem(
            base_sku=response.css("h3.t4s-sku-value ::text").get(),
            identifier=script_data.get("productID"),
            title=response.css("h1.t4s-product__title::text").get(),
            description_text=self.get_description(response),
            available=self.check_availability(response),
            old_price_text=self.typecast_price(response.css("span.money::text").getall()[1]),
            new_price_text=self.typecast_price(response.css("span.money::text").getall()[1]),
            category_names=response.meta["parent_categories_list"],
            image_urls=self.get_image(response),
            use_size_level_prices=False
        )
        colors = response.css("a.cstm-tooltip")

        if not colors:
            item["size_infos"]=self.get_sizes(response, response.css("h3.t4s-sku-value ::text").get())
            yield item
            return

        for color in colors:
            color_item = item.copy()
            color_item["color_name"] = color.css("span.tooltiptext::text").get()
            url = color.css("::attr(href)").get()
            yield response.follow(url, self.parse_color, meta={"item": color_item})

    def parse_color(self, response):
        item = response.meta["item"]
        sku = response.css("h3.t4s-sku-value ::text").get()
        item["image_urls"] = self.get_image(response)
        item["available"] = self.check_availability(response)
        item["base_sku"] = sku[0: 9]
        item["color_code"] = sku[9: len(sku)]
        item["size_infos"]=self.get_sizes(response, sku)

        yield item

    def get_sizes(self, response, sku):
        sizes_response = response.css("script.pr_variants_json::text").get()
        sizes = json.loads(sizes_response) if sizes_response else []
        size_items = []

        for size in sizes:
            size_item = SizeItem()
            size_item["size_name"] = size.get("name")
            size_item["size_identifier"] = size.get("name") + sku
            size_item["stock"] = size.get("inventory_quantity") > 0
            size_items.append(size_item)

        return size_items

    def get_script_data(self, response):
        script_data = response.css('script[type="application/ld+json"]::text').getall()[3]
        script_data = json.loads(script_data)
        return script_data

    def check_availability(self, response):
        stock_data = response.css("div[data-product-featured]::attr(data-product-featured)").get()
        stock_data = json.loads(stock_data) if stock_data else {}
        return stock_data.get("available")

    def typecast_price(self, value):
        if isinstance(value, str):
            striped_price = value.strip("Rs.")
            price = striped_price.replace(',', '')
            return float(price)
        
        return value
        
    def get_description(self, response):
        script_data = self.get_script_data(response)
        description = script_data.get("description")
        return description.replace("&amp;amp;", "&") if description else ""
    
    def get_image(self, response):
        selector = "div.t4s-product__media img.t4s-lz--fadeIn::attr(data-src)"
        image_urls = response.css(selector).getall()
        return [f"https:{img.split('?')[0]}" for img in image_urls]
