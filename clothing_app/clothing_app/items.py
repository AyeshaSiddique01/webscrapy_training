# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class ClothingAppItem(Item):
    pass


class ProductItem(Item):
    name = Field()
    price = Field()
    in_stock = Field()
    category_names = Field()
    items_size = Field()
    items_colors = Field()
    details = Field()
    image_url = Field()


class ItemSize(Item):
    size_id = Field()
    in_stock = Field()
    size_name = Field()


class ItemColor(Item):
    item_color = Field()
    url = Field()
    image_urls = Field()
    in_stock = Field()
