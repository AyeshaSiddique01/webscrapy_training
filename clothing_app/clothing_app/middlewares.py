# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import base64
from urllib.parse import unquote, urlunparse
from urllib.request import _parse_proxy

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.utils.python import to_bytes

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


class RotateProxyMiddleware(object):
    def __init__(self, proxies_path):
        self.proxy_manager = ProxyManager()
        self.proxies = []

        with open(proxies_path, "r", encoding="utf-8") as file:
            self.proxies = [Proxy(line.strip()) for line in file]

        for proxy in self.proxies:
            self.proxy_manager.add(proxy)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        proxy_path = settings.get("PROXIES_PATH")
        return cls(proxy_path)

    def process_request(self, request, spider):
        if "proxy" not in request.meta:
            proxy = self.proxy_manager.weighted_random_selection()
            request.meta["proxy"] = proxy.name

    def process_response(self, request, response, spider):
        proxy_used = self.get_used_proxy(request)
        GOOD_STATUSES = {200, 301, 302}
        BLOCKED_STATUSES = {403, 407, 503}

        if response.status in BLOCKED_STATUSES:
            proxy_used.set_weight_zero()
        elif response.status in GOOD_STATUSES:
            proxy_used.increase_weight()
        else:
            proxy_used.reduce_weight()
        return response

    def process_exception(self, request, exception, spider):
        proxy_used = self.get_used_proxy(request)
        proxy_used.set_weight_zero()

    def get_used_proxy(self, request):
        proxy_name = request.meta.get("proxy")

        for proxy in self.proxies:
            proxy_url = self.get_proxy(proxy.name)
            if proxy_url == proxy_name:
                return proxy

        return None

    def get_proxy(self, url):
        proxy_type, user, password, hostport = _parse_proxy(url)
        proxy_url = urlunparse((proxy_type, hostport, "", "", "", ""))

        return proxy_url


class ProxyLoggingMiddleware:
    def process_request(self, request, spider):
        spider.logger.info(
            f"Request {request.url} sent with {request.meta.get('proxy')}"
        )
