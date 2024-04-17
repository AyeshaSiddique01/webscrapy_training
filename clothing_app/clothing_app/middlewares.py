# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter, is_item
from scrapy import signals

from .select_proxy import Proxy, ProxyManager


class ClothingAppSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ClothingAppDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ClothingAppProxyMiddleware(object):
    def __init__(self):
        self.proxy = None
        self.proxy_manager = ProxyManager()

        self.proxies = [
            Proxy("http://stylesage:O5s6a9jaAs@66.56.67.157:60000"),
            Proxy("http://stylesage:O5s6a9jaAs@104.148.85.158:60000"),
            Proxy("http://stylesage:O5s6a9jaAs@207.32.149.111:60000"),
            Proxy("http://stylesage:O5s6a9jaAs@192.177.5.74:60000"),
            Proxy("http://stylesage:O5s6a9jaAs@207.32.149.4:60000"),
            Proxy("http://stylesage:O5s6a9jaAs@207.32.149.22:60000"),
            Proxy("http://stylesage:O5s6a9jaAs@66.56.67.6:60000"),
            Proxy("http://stylesage:O5s6a9jaAs@104.148.85.4:60000"),
            Proxy("http://stylesage:O5s6a9jaAs@66.56.67.28:60000"),
            Proxy("http://stylesage:O5s6a9jaAs@104.148.85.127:60000"),
        ]

        for proxy in self.proxies:
            self.proxy_manager.add(proxy)

    def process_request(self, request, spider):
        if "proxy" not in request.meta:
            selected_weight = self.proxy_manager.weighted_random_selection()
            self.proxy = self.proxies[selected_weight]
            request.meta["proxy"] = self.proxy.name

    def get_proxy(self):
        return self.proxy

    def process_response(self, request, response, spider):
        GOOD_STATUSES = {200, 301, 302}
        BLOCKED_STATUSES = {403, 407, 503}

        if response.status in BLOCKED_STATUSES:
            self.proxy.select_proxy("blocked")
        elif response.status in GOOD_STATUSES:
            self.proxy.select_proxy("good")
        else:
            self.proxy.select_proxy("ok")
        return response

    def process_exception(self, request, exception, spider):
        self.proxy.select_proxy("blocked")
