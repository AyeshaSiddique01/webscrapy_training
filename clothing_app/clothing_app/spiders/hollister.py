from urllib.parse import urljoin
import copy 
import scrapy

from ..items import ProductItem, SizeItem


class HollisterSpider(scrapy.Spider):
    name = "hollister"

    countries_info = [
        ('uk', 'en', 'GBP', 'https://www.hollisterco.com/shop/uk')]

    def start_requests(self):
        url = "https://www.hollisterco.com/shop/uk"
        yield scrapy.Request(url, self.parse_categories, dont_filter=True)

    def extract_categories(self, response):
        for level1 in response.css('li.js-flyout-item'):
            cat1 = level1.css('a.rs-nav__cat-label span::text').get().strip().replace('\n', '')
            for level2 in level1.css("div.regular, div.l3-formatting"):
                cat2 = level2.css('.view-all-level2 a::text,div.rs-cat-nav__header h3::text,div.rs-cat-nav__header span::text, a.rs-nav-menu-item::text').get().strip().replace('\n', '')
                for level3 in level2.css("ul.rs-nav-cat-menu li:not(.view-all-level2)"):
                    cat3 = level3.css("a::text").get().strip().replace('\n', '')
                    url3 = level3.css("a::attr(href)").get()
                    yield {'categories': [cat1, cat2, cat3], 'url': url3}

    def parse_categories(self, response):
        for category in response.css("nav ul.nav-accordion-container--level1 li.js-flyout-item"):
            parent_category = category.css("a.rs-nav__cat-label span ::text").get().strip()
            all_subcategories = self.parse_level2(category, [parent_category])
            for category in all_subcategories:
                print("all_subcategories: ", category)

    def parse_level2(self, category, parent):
        level3_parents = category.css("li.view-all-level2 a.rs-nav-link--minor::text").getall()
        level3_parents = [parent.strip() for parent in level3_parents]

        # for level2_category in category.css("div.regular ul.nav-accordion-container--level2 li.rs-nav-item--minor"):
        for level2_category in category.css("div.regular, div.l3-formatting"):
            level2_data = level2_category.css('.view-all-level2 a::text,div.rs-cat-nav__header h3::text,div.rs-cat-nav__header span::text, a.rs-nav-menu-item::text').get().strip()
            parent_categories = copy.deepcopy(parent)
            parent_categories.append(level2_data)

            if level2_data in level3_parents:
                yield from self.parse_level3(category, parent_categories)
            else:
                url = level2_category.css("a.rs-nav-link--minor ::attr(href)").get()
                yield parent_categories, url

    def parse_level3(self, category, parent):
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

    def parse_products(self, response):
        print("--------parse_products--------")
