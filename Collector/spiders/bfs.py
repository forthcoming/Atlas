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

# 只有当函数里面出现yield关键字时，response.meta才会有depth属性

from scrapy import Spider,Request,FormRequest
import re

class BFS(Spider):
    name = "bfs"
    custom_settings = {
        'DOWNLOAD_TIMEOUT':8,
        'RETRY_TIMES':2, 
        'DEPTH_PRIORITY':1,
        'REDIRECT_PRIORITY_ADJUST':2, # Default: +2
        'RETRY_PRIORITY_ADJUST':-4,   # Default: -1
        'CONCURRENT_REQUESTS_PER_IP':6,
        'CONCURRENT_REQUESTS':6,      # 一次性读入start_urls个数，然后局部BFS，然后再进行下一轮BFS
    }

    def start_requests(self): 
        for page in range(1,5):
            yield Request(f'https://www.amazon.com/s?rh=i%3Aaps%2Ck%3ATV+%26+Video&page={page}',meta={'key':'TV & Video'})
            yield Request(f'https://www.amazon.com/s?rh=i%3Aaps%2Ck%3A4K+Ultra+HD+TVs&page={page}',meta={'key':'4K Ultra HD TVs'})
            yield Request(f'https://www.amazon.com/s?rh=i%3Aaps%2Ck%3ACurved+TVs&page={page}',meta={'key':'Curved TVs'})

    def parse(self, response):
        print('parse',response.meta['depth'],response.request.priority,response.url)
        for res in response.xpath('//li[starts-with(@id,"result_")]'):
            ASIN=res.xpath('@data-asin').extract_first()
            yield {
                'ASIN':ASIN,
                'keyWord':response.meta['key'],
            }
            yield Request(f'https://www.amazon.com/dp/{ASIN}',callback=self.detail)

    def detail(self,response):
        print('detail',response.meta['depth'],response.request.priority,response.url)
        inputs=response.xpath( '//form[@id="addToCart"]')
        unicorn=response.xpath('string(//tr[contains(.,"Best Sellers Rank")] | //li[contains(.,"Best Sellers Rank")])').extract_first()
        unicorn=re.search(r'#([0-9,]+)\sin\s([a-zA-Z& ,]+)',unicorn)
        rank=category=''
        if unicorn:
            rank=''.join(unicorn.group(1).split(','))
            category=unicorn.group(2).strip()
        item= {
            'ASIN': inputs.xpath('input[@id="ASIN"]/@value').extract_first(),
            'rank':rank,
            'category':category,
        }
        if item['ASIN']:
            yield FormRequest(
                url='https://www.amztracker.com/unicorn.php',
                formdata={'rank': rank, 'category': category},
                method='GET',
                meta={'item':item},
                callback=self.amztracker,
                dont_filter=True,
                )

    def amztracker(self,response):
        print('amztracker',response.meta['depth'],response.request.priority,response.url)
