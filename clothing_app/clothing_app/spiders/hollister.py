import copy
import json
import re

import scrapy
import scrapy.resolver

from ..items import ProductItem, SizeItem


class HollisterSpider(scrapy.Spider):
    name = "hollister"
    page_size = 90

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "priority": "u=0, i",
        "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }

    cookies = {
        "geoLocation": "GB:US:",
    }

    def start_requests(self):
        countries_info = [
            ("uk", "en", "GBP", "https://www.hollisterco.com/shop/uk")]

        for country_info in countries_info:
            country, lang, currency, country_url = country_info
            meta = {
                "country": country,
                "lang": lang,
                "currency": currency
            }
            yield scrapy.Request(
                country_url,
                self.parse_categories,
                meta=meta,
                dont_filter=True,
                headers=self.headers,
                cookies=self.cookies,
            )

    def parse_categories(self, response):
        for category in response.css("nav ul.nav-accordion-container--level1 li.js-flyout-item"):
            parent_category = category.css("a.rs-nav__cat-label span ::text").get().strip()
            all_subcategories = self.parse_level2_categories(
                category, [parent_category])

            for category in all_subcategories:
                cat, url = category
                absolute_url = response.urljoin(url)
                response.meta.update({"parent": cat})

                yield scrapy.Request(
                    absolute_url,
                    self.parse_paginantion,
                    meta=response.meta,
                    headers=self.headers,
                    cookies=self.cookies
                )

    def parse_level2_categories(self, category, parent):
        level3_parents = category.css("li.view-all-level2 a.rs-nav-link--minor::text").getall()
        level3_parents = [parent.strip() for parent in level3_parents]

        for level2_category in category.css("div.regular ul.nav-accordion-container--level2 li.rs-nav-item--minor"):
            level2_selector = ".view-all-level2 a::text,div.rs-cat-nav__header h3::text,div.rs-cat-nav__header span::text, a.rs-nav-menu-item::text"
            level2_data = level2_category.css(level2_selector).get().strip()
            parent_categories = copy.deepcopy(parent)
            parent_categories.append(level2_data)

            if level2_data in level3_parents:
                yield from self.parse_level3_categories(category, parent_categories)
            else:
                url = level2_category.css("a.rs-nav-link--minor ::attr(href)").get()
                yield parent_categories, url

    def parse_level3_categories(self, category, parent):
        for level3_category in category.css("ul.nav-accordion-container--level3"):
            parent_category = None

            for level3_subcategory in level3_category.css("li.rs-nav-item--minor"):
                if not parent_category:
                    parent_category = level3_subcategory.css("li.view-all-level2 a::text").get().strip()
                    if not parent_category or parent_category != parent[-1]:
                        break
                elif parent_category == parent[-1]:
                    parent_categories = copy.deepcopy(parent)
                    level3_data = level3_subcategory.css("a.rs-nav-link--minor ::text").get().strip()
                    parent_categories.append(level3_data)
                    url = level3_subcategory.css("a.rs-nav-link--minor ::attr(href)").get()
                    yield parent_categories, url

    def parse_paginantion(self, response):
        total_products = int(response.css("div.products ::attr(data-result-total)").get() or 0)
        no_of_pages = -(-total_products // self.page_size)

        for i in range(no_of_pages):
            absolute_url = response.urljoin(f"?filtered=true&rows=90&start={i*self.page_size}")
            yield scrapy.Request(
                absolute_url,
                self.parse_products,
                meta=response.meta,
                headers=self.headers,
                cookies=self.cookies
            )

    def parse_products(self, response):
        products_selector = "ul.product-grid__products li.catalog-productCard-module__productCard"
        for product in response.css(products_selector):
            product_url = product.css("a.catalog-productCard-module__product-content-link ::attr(href)").get()
            absolute_url = response.urljoin(product_url)
            yield scrapy.Request(
                absolute_url,
                self.parse_color,
                meta=response.meta,
                headers=self.headers,
                cookies=self.cookies
            )

    def parse_color(self, response):
        if not response.css("div.soldout-wrap"):
            data = self.get_script_data(response)
            size_data = self.process_size_data(data)

            for product_color in data["products"]:
                item = ProductItem()
                item["identifier"] = product_color["productId"]
                item["size_infos"] = self.get_size_infos(size_data[item["identifier"]])
                item["available"] = self.get_availability(item["size_infos"])
                item["url"] = response.url
                item["country_code"] = response.meta["country"]
                item["currency"] = response.meta["currency"]
                item["language_code"] = response.meta["lang"]
                item["category_names"] = response.meta["parent"]

                yield from self.parse_item(item, product_color)

    def parse_item(self, item, product_info):
        old_price_text, new_price_text = self.get_prices(product_info)
        item["old_price_text"] = old_price_text
        item["new_price_text"] = new_price_text
        item["brand"] = product_info["brand"]
        item["description_text"] = product_info["longDescription"]
        item["title"] = product_info["productName"]
        item["base_sku"] = product_info["kicId"].split("_")[-1]
        item["color_name"] = product_info["colorFamily"]
        item["color_code"] = product_info["kicId"].split("-")[-1]
        item["image_urls"] = self.get_images(product_info)
        item["use_size_level_prices"] = False

        yield item

    def get_size_infos(self, data):
        size_infos = []

        for size in data:
            size_infos.append(
                SizeItem(
                    stock=1 if size["inventory"] else 0,
                    size_name=size["fullSizeLabel"],
                    size_identifier=size["shortSku"],
                )
            )
        return size_infos

    def process_size_data(self, data):
        size_data = {}

        for size in data["skus"]:
            size_data.setdefault(size["productId"], []).append(size)
        return size_data

    def get_availability(self, size_infos):
        return any(size["stock"] for size in size_infos)

    def get_images(self, product_color):
        image_set = product_color["imageSet"]
        images = sum(image_set.get(s) or [] for s in ["prod", "ugc", "life", "model"])
        
        return [image["mainImageSrc"] for image in images]

    def get_prices(self, data):
        prices = data["prices"]["list"]
        old_price_text = prices["originalPrice"]
        new_price_text = prices["discountPrice"] if prices["discountPrice"] else old_price_text

        return old_price_text, new_price_text

    def get_script_data(self, response):
        script_data = response.css('script:contains("APOLLO_STATE__product")::text').get()
        script_data = re.findall(r"({.*})", script_data)
        json_data = json.loads(script_data[0])
        data = json_data["CACHE"]["ROOT_QUERY"]
        key = [k for k in data.keys() if "collection" in k and "faceout" in k]

        return data[key[0]]
