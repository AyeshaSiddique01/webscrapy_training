import json
import urllib.request

import scrapy

from ..items import ProductItem, SizeItem


class SelectedSpider(scrapy.Spider):
    name = "selected"

    def start_requests(self):
        url = "https://www.selected.com/en-gb/homme/trousers/loose-fit-tapered-trousers-16082851_BoneWhite.html?clickedFromCategory=sl-homme-collection-trousers-loose"
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        data = self.get_json_data(response)
        item = ProductItem(
            url=response.url,
            base_sku=data.get("articleNumber"),
            identifier=data.get("id"),
            title=data.get("name"),
            brand=data.get("brand"),
            description_text=self.get_product_description(response),
            available=data.get("inStockFlag"),
            old_price_text=data.get("price"),
            new_price_text=data.get("salesPrice"),
            currency=data.get("currency"),
            category_names=data.get("category"),
            image_urls=self.get_images_url(response),
            use_size_level_prices=False
        )
        response.meta.update({"item": item})
        yield from self.parse_variant(response)

    def parse_variant(self, response):
        data_urls = self.get_color_data_urls(response)
        item = response.meta["item"]

        for url in data_urls:
            data = self.get_dataurl_data(url)
            item_colors = data["product"]["variationAttributes"][0]["values"]

            for item_color in item_colors:
                if item_color["selected"]:
                    item["color_name"] = item_color["displayValue"]
                    item["available"] = data["product"]["available"]
                    item["image_urls"] = self.get_color_images(item_color)
                    item["size_infos"] = self.get_size_infos(data)
                    yield item

    def get_json_data(self, response):
        data = response.css('script ::text').getall()[3]
        data = data.strip()
        json_string = data[data.index('[')+1:-2]
        json_data = json.loads(json_string)
        product_data = json_data["ecommerce"]["detail"]["products"][0]
        product_data["currency"] = json_data["ecommerce"]["currencyCode"]
        return product_data

    def get_dataurl_data(self, url):
        json_length = urllib.request.urlopen(url) if url else None
        if json_length:
            return json.loads(json_length.read())
        return {}

    def get_images_url(self, response):
        script_data = response.css(
            'script[type="application/ld+json"]::text').get().strip("\n")
        data = json.loads(script_data) if script_data else {}
        return data.get("image")

    def get_color_images(self, item_color):
        images = item_color["images"]["swatch"]
        return [image["url"] for image in images]

    def get_product_description(self, response):
        description = response.css("div.product-content__text::text").get()
        return description or ""

    def get_color_data_urls(self, response):
        data_url = response.css("button.product-attribute__button--color-swatch ::attr(data-url)").getall()
        return data_url

    def get_size(self, json_size, length):
        if json_size:
            item_size = SizeItem(
                size_identifier=f"{length} - {json_size['id']}",
                size_name=json_size["displayValue"],
                stock=json_size["isAvailable"],
            )
            return item_size

    def get_length_size_infos(self, size_infos, length):
        item_size_infos = []
        for size in size_infos:
            if size["selectable"]:
                item_size = self.get_size(size, length)
                item_size_infos.append(item_size)
        return item_size_infos

    def get_size_infos(self, data):
        lengths = data["product"]["variationAttributes"][2]["values"]
        item_size_infos = []

        for length in lengths:
            length_data = self.get_dataurl_data(length["url"])
            size_infos = length_data["product"]["variationAttributes"][1]["values"]
            item_size_infos += self.get_length_size_infos(size_infos, length['id'])

        return item_size_infos
