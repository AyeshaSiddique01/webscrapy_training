import copy
import json
from urllib.parse import urljoin

import scrapy

from ..items import ProductItem, SizeItem


class AckermansSpider(scrapy.Spider):
    name = "ackermans"

    def start_requests(self):
        url = "https://www.ackermans.co.za/"
        yield scrapy.Request(url, self.parse)

    navigation_api = "https://www.ackermans.co.za/api/startup-data.json"
    products_api = "https://www.ackermans.co.za/graphql?operationName=products_listAndAggregations"
    product_data_api = "https://www.ackermans.co.za/graphql?operationName=products_pdp"
    product_base_url = "https://www.ackermans.co.za/products/"
    product_image_base_url = "https://www.ackermans.co.za/imagekit/prod-ack-product-images/"


    page_size = 20

    products_headers = {
        "Content-Type": "application/json",
        "accept": "application/json, text/plain, */*",
    }

    def parse(self, response):
        yield scrapy.Request(self.navigation_api, self.parse_home_page)

    def parse_home_page(self, response):
        categories = json.loads(response.text)["categories"][0]

        for category in self.filter_menu_categories(categories.get("children")):
            if category["name"] == "Promotions":
                continue
            yield from self.parse_childrens(response, category, [category])

    def parse_childrens(self, response, categories, parents):

        for category in self.filter_menu_categories(categories["children"]):
            parent_categories_list = copy.deepcopy(parents)
            parent_categories_list.append(category)

            if self.is_children_exists(category.get("children")):
                yield from self.parse_childrens(response, category, parent_categories_list)
            else:
                yield self.make_nav_request(response, parent_categories_list)

    def make_nav_url(self, categories):
        url = self.product_base_url
        for child in categories:
            url = urljoin(url, f"{child['url_key']}/")
        return url

    def make_nav_request(self, response, categories):
        if categories:
            meta = copy.deepcopy(response.meta)
            meta["url"] = self.make_nav_url(categories)
            meta["categories"] = [child["name"] for child in categories]
            meta["category_id"] = categories[-1]["id"]

            return self.make_graphql_category_request(meta, 1, self.parse_pagination)

    def parse_pagination(self, response):
        data = json.loads(response.text)
        yield self.parse_products(response, data)

        total_products = data["data"]["products"]["total_count"]
        no_of_pages = -(-total_products // self.page_size)
        for i in range(1, no_of_pages + 1):
            yield self.make_graphql_category_request(response.meta, i, self.parse_products)

    def parse_products(self, response, data=None):
        if not data:
            data = json.loads(response.text)

        products = data["data"]["products"]["items"]
        if products:
            for product in products:
                meta = copy.deepcopy(response.meta)
                meta["url_key"] = product["url_key"]
                return self.make_graphql_product_request(meta, self.parse_product_details)

    def parse_product_details(self, response):
        data = json.loads(response.text)
        item_data = data["data"]["products"]["items"][0]

        item = ProductItem()
        item["url"] = response.url
        item["base_sku"] = item_data["sku"]
        item["identifier"] = item_data["id"]
        item["title"] = item_data["name"]
        item["description_text"] = item_data["meta_description"]
        item["available"] = item_data["stock_status"] == "IN_STOCK"
        item["old_price_text"] = item_data["price_range"]["minimum_price"]["regular_price"]["value"]
        item["new_price_text"] = item_data["price_range"]["minimum_price"]["final_price"]["value"]
        item["category_names"] = response.meta["categories"]
        item["image_urls"] = self.get_images(item_data)
        item["size_infos"] = self.get_sizes_info(item_data)
        item["use_size_level_prices"] = False

        response.meta.update({"item": item, "item_data": item_data})
        yield from self.parse_color(response)

    def parse_color(self, response):
        item_data = response.meta["item_data"]
        item = response.meta["item"]

        item_color = item_data["colour"]
        if item_color:
            item["color_name"] = item_color
            yield item
            return

        variants = item_data["variants"]
        colors = {variant["attributes"][0]["label"] for variant in variants}

        if len(colors) == 1:
            item["color_name"] = colors.pop()
            yield item
            return

        for color in colors:
            yield from self.parse_color_variant(item, variants, color)

    def parse_color_variant(self, item, variants, color):
        color_sizes = []
        item["color_name"] = color

        for variant in variants:
            if variant["attributes"][0]["label"] == color:
                color_sizes.append(self.get_size(variant))
        item["size_infos"] = color_sizes
        yield item

    def filter_menu_categories(self, categories):
        return [category for category in categories if category.get("include_in_menu")]

    def is_children_exists(self, item):
        return any(child.get("include_in_menu") for child in item)

    def get_images(self, item_data):
        images = item_data["media_gallery"]
        return [self.product_image_base_url+image['file_name'] for image in images]


    def get_sizes_info(self, item_data):
        item_size = item_data["productsize"]
        if item_size:
            return item_size

        sizes_data = item_data["variants"]
        return [self.get_size(size) for size in sizes_data]

    def get_size(self, size):
        return SizeItem(
            size_original_price_text=size["product"]["price_range"]["minimum_price"]["regular_price"]["value"],
            size_current_price_text=size["product"]["price_range"]["minimum_price"]["final_price"]["value"],
            size_identifier=size["product"]["id"],
            size_name=size["attributes"][1]["label"].strip(),
            stock=size["product"]["stock_status"] == "IN_STOCK",
        )

    def make_graphql_category_request(self, meta, page, callback):
        payload = self.get_category_payload(meta["category_id"], page)

        return scrapy.Request(
            self.products_api,
            callback=callback,
            body=json.dumps(payload),
            method="POST",
            meta=meta,
            headers=self.products_headers,
            dont_filter=True,
        )

    def make_graphql_product_request(self, meta, callback):
        payload = self.get_product_payload(meta["url_key"])

        return scrapy.Request(
            self.product_data_api,
            callback=callback,
            body=json.dumps(payload),
            method="POST",
            meta=meta,
            headers=self.products_headers,
            dont_filter=True,
        )

    def get_category_payload(self, category_id, page):
        return {
            "operationName": "products_listAndAggregations",
            "variables": {},
            "query": "query products_listAndAggregations {\n  products(\n    filter: {category_id: "
            "{eq: \""+str(category_id)+"\"}}\n    search: \"\"\n    sort: {}\n    pageSize: 20\n   "
            " currentPage: "+str(page)+"\n  ) {\n    items {\n      __typename\n      id\n      sku"
            "\n      stock_status\n      name\n      description {\n        html\n        __typenam"
            "e\n      }\n      product_attribute\n      product_decal\n      media_gallery {\n     "
            "   file_name\n        label\n        position\n        disabled\n        __typename\n "
            "     }\n      price_range {\n        minimum_price {\n          ...AllPriceFields\n   "
            "       __typename\n        }\n        __typename\n      }\n      url_key\n      meta_t"
            "itle\n      meta_description\n      categories {\n        id\n        __typename\n    "
            "  }\n    }\n    total_count\n    aggregations(filter: {category: {includeDirectChildre"
            "nOnly: true}}) {\n      attribute_code\n      count\n      label\n      options {\n   "
            "     count\n        label\n        value\n        __typename\n      }\n      __typenam"
            "e\n    }\n    sort_fields {\n      default\n      options {\n        label\n        va"
            "lue\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nf"
            "ragment AllPriceFields on ProductPrice {\n  final_price {\n    value\n    __typename\n"
            "  }\n  regular_price {\n    value\n    __typename\n  }\n  __typename\n}\n"}
    
    def get_product_payload(self, url_key):
        return {
            "operationName":"products_pdp",
            "variables":{"urlKey":url_key},
            "query":"query products_pdp($urlKey: String) {\n  products(filter: {url_key: {eq: $urlKey}"
            "}) {\n    items {\n      __typename\n      id\n      sku\n      name\n      description {"
            "\n        html\n        __typename\n      }\n      price_range {\n        minimum_price {"
            "\n          ...AllPriceFields\n          __typename\n        }\n        __typename\n     "
            " }\n      url_key\n      meta_title\n      meta_description\n      stock_status\n      pr"
            "oduct_attribute\n      product_decal\n      categories {\n        id\n        name\n     "
            "   url_path\n        __typename\n      }\n      related_products {\n        sku\n        "
            "__typename\n      }\n      media_gallery {\n        file_name\n        label\n        pos"
            "ition\n        disabled\n        __typename\n      }\n      size_guide\n      washcare_gu"
            "ide\n      manufacturer\n      product_attribute\n      product_decal\n      colour\n    "
            "  gender\n      pim_product_category\n      pim_size_guide\n      pim_wash_care_guide\n  "
            "    primarycolour\n      productsize\n      sizesortseq\n      ... on ConfigurableProduct"
            " {\n        variants {\n          product {\n            id\n            sku\n           "
            " price_range {\n              minimum_price {\n                ...AllPriceFields\n       "
            "         __typename\n              }\n              __typename\n            }\n          "
            "  stock_status\n            sizesortseq\n            __typename\n          }\n          a"
            "ttributes {\n            label\n            code\n            value_index\n            ui"
            "d\n            __typename\n          }\n          __typename\n        }\n        __typena"
            "me\n      }\n    }\n    __typename\n  }\n}\n\nfragment AllPriceFields on ProductPrice {\n"
            "  discount {\n    ...ProductDiscountFields\n    __typename\n  }\n  final_price {\n    ..."
            "MoneyFields\n    __typename\n  }\n  regular_price {\n    ...MoneyFields\n    __typename\n"
            "  }\n  __typename\n}\n\nfragment ProductDiscountFields on ProductDiscount {\n  amount_off"
            "\n  percent_off\n  __typename\n}\n\nfragment MoneyFields on Money {\n  value\n  __typenam"
            "e\n}\n"}
