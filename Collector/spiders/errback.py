# REDIRECT_PRIORITY_ADJUST
# Default: +2
# Scope: scrapy.downloadermiddlewares.redirect.RedirectMiddleware
# Adjust redirect request priority relative to original request:
# a positive priority adjust (default) means higher priority.
# a negative priority adjust means lower priority.

# RETRY_PRIORITY_ADJUST
# Default: -1
# Scope: scrapy.downloadermiddlewares.retry.RetryMiddleware
# Adjust retry request priority relative to original request:
# a positive priority adjust means higher priority.
# a negative priority adjust (default) means lower priority.

# priority (int) – the priority of this request (defaults to 0). 
# The priority is used by the scheduler to define the order used to process requests. 
# Requests with a higher priority value will execute earlier. Negative values are allowed in order to indicate relatively low-priority.

# DEPTH_PRIORITY
# Default: 0
# Scope: scrapy.spidermiddlewares.depth.DepthMiddleware
# An integer that is used to adjust the request priority based on its depth:
# if zero (default), no priority adjustment is made from depth
# a positive value will decrease the priority, i.e. higher depth requests will be processed later ; this is commonly used when doing breadth-first crawls (BFO)
# a negative value will increase priority, i.e., higher depth requests will be processed sooner (DFO)
# This setting adjusts priority in the opposite way compared to other priority settings REDIRECT_PRIORITY_ADJUST and RETRY_PRIORITY_ADJUST.

# By default, Scrapy uses a LIFO queue for storing pending requests, which basically means that it crawls in DFO order. 
# This order is more convenient in most cases. If you do want to crawl in true BFO order, you can do it by setting the following settings:
# DEPTH_PRIORITY = 1
# SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
# SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'

# 一旦发生重定向,DUPEFILTER_CLASS会把所有重定向过的url都记录下来
#只有当函数里面出现yield关键字时，response.meta才会有depth属性

from scrapy import Spider,Request
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import TimeoutError, TCPTimedOutError,DNSLookupError,ConnectionRefusedError

class Errback(Spider):
    name = "errback"
    start_urls = [
        # "http://www.httpbin.org",               # HTTP 200 expected
        # "http://www.httpbin.org/status/403",     # FORBIDDEN
        # "http://www.httpbin.org/status/404",    # NOT FOUND
        # "http://www.httpbin.org/status/503",    # SERVICE UNAVAILABLE,受RETRY_TIMES和DOWNLOAD_TIMEOUT影响,先retry,再进入failure.check(HttpError)
        # "http://www.httpbin.org/status/500",    # INTERNAL SERVER ERROR
        "http://www.httpbin.org:12345",         # Timeout Error,有时可能是ConnectionRefusedError
        # "http://www.httphttpbinbin.org",        # DNS error expected

    ]
    custom_settings = {
        'RETRY_TIMES':3,          # Default: 2 Maximum number of times to retry,每次重试请求都会经过自定义的DownloadMiddleware,无须加dont_filter=True属性
        'DOWNLOAD_TIMEOUT':.9,     # 注意该参数如果过小，会影响到网页抛出的异常
        'DEPTH_PRIORITY':1,       # BFS
        'SCHEDULER_DISK_QUEUE':'scrapy.squeues.PickleFifoDiskQueue',
        'SCHEDULER_MEMORY_QUEUE':'scrapy.squeues.FifoMemoryQueue',
    }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url,callback=self.parse,errback=self.errback_httpbin,dont_filter=True,meta={'item':{'name':'avatar','age':11}})

    def parse(self, response):
        print(f'Got successful response from {response.url}',response.status,response.meta)

    def errback_httpbin(self, failure): # get all failures
        print(repr(failure))
        if failure.check(HttpError):    # you can get the non-200 response
            response = failure.value.response
            print(f'HttpError on {response.url}', response.status,response.request.priority,response.meta,response.request.callback.__name__)
            if response.meta['depth']<3:
                yield failure.request #每次请求都会经过自定义的DownloadMiddleware,无须加dont_filter=True属性
        elif failure.check(DNSLookupError):
            request = failure.request  # this is the original request
            print(f'DNSLookupError on {request.url}',request.meta,request.callback.__name__)
        elif failure.check(TimeoutError,TCPTimedOutError,ConnectionRefusedError):
            request = failure.request   
            print(f'TimeoutError on {request.url}',request.priority,request.meta,request.callback.__name__)  #只在最后一次超时后才执行
        else:
            request = failure.request   
            print(f'UnknownError on {request.url}',request.callback.__name__)
