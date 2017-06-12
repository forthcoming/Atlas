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
        'RETRY_TIMES':3,            # Default: 2 Maximum number of times to retry,每次重试请求都会经过自定义的DownloadMiddleware,无须加dont_filter=True属性
        'RETRY_PRIORITY_ADJUST':-4, # Default: -1    
        'DOWNLOAD_TIMEOUT':.9,      # 注意该参数如果过小，会影响到网页抛出的异常
        'DEPTH_PRIORITY':1,         # BFS
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
