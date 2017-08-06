from scrapy.spiders import Spider
from scrapy import Request, FormRequest
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import TimeoutError, TCPTimedOutError, DNSLookupError, ConnectionRefusedError
import re
from Spider.utils.dictionary import key
from urllib.parse import quote

RETRY = 8  # 数字越小速度越快，数据丢失越严重
unicornHeader = {
    'Host': 'www.amztracker.com',
    'Referer': 'https://www.amazon.com',
}

# detail+error-callback=parse=galance
class Amazon(Spider):
    name = "amazon"
    allowed_domains = ['amazon.com', 'amztracker.com']
    custom_settings = {
        #'LOG_LEVEL':'INFO',
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,  # enabled by default
        'DEFAULT_REQUEST_HEADERS': {
            'Referer': 'https://www.amazon.com',
        },
        'ITEM_PIPELINES': {
            'Spider.pipelines.ImagePipeline':1, # Settings中的ITEM_PIPELINES不再有效
            'Spider.pipelines.JsonPipeline': 300,
            # 'Spider.pipelines.MongoPipeline': 300,
        },
        'IMAGES_STORE':'../photo',    # 没有则新建,已经存在的图片不会再下载
        'IMAGES_EXPIRES':90,          # 单位是天，调整失效期限，避免下载最近已经下载的图片
        'DOWNLOADER_MIDDLEWARES': {
            'Spider.utils.middlewares.ProxiesMiddleware': 400,
            'Spider.utils.middlewares.HeadersMiddleware': 543,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        },

        'DEPTH_PRIORITY': 1,  # BFS，是以starts_url为准，局部BFS，受CONCURRENT_REQUESTS影响
        'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue',
        'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue',

        'REDIRECT_PRIORITY_ADJUST':2, # Default: +2
        'RETRY_PRIORITY_ADJUST': -1,  # Default: -1
        'RETRY_TIMES': 4, # Default: 2, can also be specified per-request using max_retry_times attribute of Request.meta
        'DOWNLOAD_TIMEOUT': 25, # This timeout can be set per spider using download_timeout spider attribute and per-request using download_timeout Request.meta key

        # 以下是为scrapy_redis设置的
        # 'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",
        # 'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
        # 'SCHEDULER_PERSIST': False,  # Don't cleanup redis queues, allows to pause/resume crawls.

        'CONCURRENT_REQUESTS': 30,  # default 16,Scrapy downloader 并发请求(concurrent requests)的最大值,即一次读入并请求的url数量
        # 'CONCURRENT_REQUESTS_PER_DOMAIN':15,  #default 8 ,对单个网站进行并发请求的最大值。
        'CONCURRENT_REQUESTS_PER_IP': 15,  # default 0,如果非0，则忽略CONCURRENT_REQUESTS_PER_DOMAIN 设定， 也就是说并发限制将针对IP，而不是网站
        'REACTOR_THREADPOOL_MAXSIZE': 10,  # default 10
    }

    def start_requests(self):
        for each in key:
            yield Request(
                url=f'https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords={quote(each)}',
                meta={'key':each,'dont_redirect':True},
                callback=self.parse,
                errback=self.error
            )

    def parse(self, response):
        url=response.xpath('//*[@id="pagn"]//a/@href').extract_first(default='')    
        url=re.sub(r'&qid=.+&spIA=.+','',url,count=1)  # 去掉不必要的内容，以便达到更好的去重效果
        # number=response.xpath('//*[@id="pagn"]/span[@class="pagnDisabled"]/text()').extract_first() 
        number=response.xpath('string(//*[@id="pagn"])').re(r'\d+') # number重要，所以要确保正确得到总页数
        if number and url:
            count=int(response.xpath('//*[@id="s-result-count"]/text()').re_first(r'[0-9,]+ of ([0-9,]+)','0').replace(',',''))
            yield {'number':int(number[-1]),'url':url,'key':response.meta['key'],'count':count}
            for page in range(1,int(number[-1])+1):   
                yield response.follow(
                    url=re.sub(r'page=\d+',f'page={page}',url,count=1),
                    meta={'dont_redirect':True,'key':response.meta['key']}, # 基本信息页容易被重定向到无数据页面,同时增加了请求量,301会被errback函数捕捉到
                    callback=self.galance,  # 到达galance后大部分深度都是1,极少部分会是2,或者3等,但不会很大,基本没什么影响
                    errback=self.error
                )   
        elif response.meta['depth'] < RETRY:
            request = response.request
            request.dont_filter = True
            yield request  # 自动增加深度
        else:
            yield {'url': response.url, 'error': 'StartError', 'key': response.meta['key']}  # 日志用 

    def galance(self, response):
        lis = response.xpath('//li[starts-with(@id,"result_")]')
        if lis:
            for res in lis:
                ASIN = res.xpath('@data-asin').extract_first()  # It returns None if no element was found
                avgStar = res.xpath('string(//*[@name=$val])', val=ASIN).extract_first(default='0')
                avgStar = re.search(r'(\d+\.\d+ |\d+)', avgStar)
                sellers = 0
                for each in res.xpath('.//*[contains(.,"offer")]//text()').extract():
                    result = re.findall(r'(\d+)\s.*?offer', each)  # 一个卖家显示offer，多个卖家显示offers
                    if result:
                        sellers = sum(int(num) for num in result)
                item= {
                    '_id': ASIN,  # 防止MongoDB生成_id字段
                    'title': res.xpath('.//a[@title]/@title').extract_first(),
                    'brand': res.xpath('string(div/div/div/div[2]/div[last()-1]/div[2])').extract_first(default=''),
                    'avgStar':res.xpath('string(//*[@name=$val])', val=ASIN).extract_first(default='0'),
                    'totalReviews': res.xpath('//*[@name=$val]/following-sibling::a/text()', val=ASIN).extract_first(default='0'),
                    'sellers': sellers,
                    'price': res.xpath( './/span[@aria-label]/@aria-label | .//span[contains(.,"$")]/text()').extract_first(default='0'),
                    'key': response.meta['key'],
                    'url': response.url,
                    'resultID':int(res.xpath('@id').re_first(r'result_(\d+)')),
                    'image_url':res.xpath('.//img/@src').extract_first(),
                }
                #通过日志发现,允许商品重定向更好些
                yield Request(f'https://www.amazon.com/dp/{ASIN}', callback=self.detail, errback=self.error,meta={'item':item},) # 重复的ASIN请求会被自动丢掉
        elif response.meta['depth'] < RETRY:
            request = response.request
            request.dont_filter = True
            yield request  # 自动增加深度
        else:
            yield {'url': response.url, 'error': 'NO_LI', 'key': response.meta['key']}  # 日志用

    def detail(self, response):
        color=dimension=rank = category=showtime=''  
        # 获取color,dimension,showtime开始  
        # ids = response.xpath('//*[@id="prodDetails" or @id="detail-bullets"]//text()').extract()
        res = response.xpath('string(//*[@id="variation_color_name"]/div[1])').extract_first('')
        res = re.search(r'Color:\s*(.+)', ''.join(res.split()))
        if res:
            color=res.group(1)
        ids = response.xpath('//*[@id="prodDetails"]//text() | //*[@id="detail-bullets"]//text()').extract() # 注意|和or的区别
        arr=[each.strip() for each in ids if each.strip()]
        for index,_ in enumerate(arr[:-1]):
            if 'Size' in _:
                dimension=arr[index+1]
            if 'Dimensions' in _ and not dimension:
                dimension=arr[index+1]
            if 'Color' in _ and not color:
                color=arr[index+1]
            if 'Date first available' in _:
                showtime=arr[index+1]
        # 获取color,dimension,showtime结束,获取rank,category开始
        unicorn = response.xpath('string(//*[contains(.,"Best Sellers Rank")])').extract_first()
        
        result = re.search(r'#([0-9,]+)\s\w*\s*in\s([a-zA-Z& ,]+)', unicorn)
        rank = category = ''
        if result:
            rank = ''.join(result.group(1).split(','))
            category = result.group(2).strip()
        # 获取rank,category结束   
        inputs = response.xpath('//form[@id="addToCart"]')
        item=response.meta['item']
        item.update({
                    'soldBy': ' '.join(response.xpath('string(//*[@id="merchant-info"])').extract_first(default='').split()),
                    'merchantID': inputs.xpath('input[@id="merchantID"]/@value').extract_first(),
                    'rank': rank,
                    'category': category,
                    'color':color,
                    'dimension':dimension,
                    'showtime':showtime,
                    'sales':'',  # 先给个默认值
                    }
              )
        result=re.findall(r'#([0-9,]+)\s\w*\s*in\s([a-zA-Z& ,>]+)',unicorn)
        for index,each in enumerate(result[1:],1):
            item[f'rank{index}']=float(''.join(each[0].split(',')))      
            item[f'category{index}']=each[1].split('>')[-1].strip()

        if rank and category:
            if not(item['brand'] or item['sellers']):  # 注意位置 
                item['sellers']=1
                item['price']=response.xpath('//*[@id="priceblock_ourprice" or @id="priceblock_saleprice"]/text()').extract_first(default='0')
            if not item['title']:
                item['title']=response.xpath('string(//*[@id="productTitle" or contains(@class,"product-title")])').extract_first().strip()
            if not item['brand']:
                item['brand']=response.xpath('string(//*[@id="centerCol"]/div[1]/div[1])').extract_first(default='').strip()
            if not item['totalReviews']:
                item['totalReviews']=response.xpath('//*[contains(@class,"totalReviewCount")]/text()').extract_first(default='0')
            if not item['avgStar']:
                item['avgStar']=response.xpath('//*[@id="acrPopover"]/@title').extract_first(default='0')
            yield FormRequest(
                url='https://www.amztracker.com/unicorn.php',
                headers=unicornHeader,
                formdata={'rank': rank, 'category': category},
                method='GET',
                meta={'item': item},
                callback=self.amztracker,
                errback=self.error,  # 本项目中这里触发errback占绝大多数
                dont_filter=True,  # 要加此参数
            )
            
        elif response.meta['depth'] < RETRY:
            request = response.request
            request.dont_filter = True
            yield request  # 自动增加深度
        else:
            yield item
            yield {'url': response.url, 'error': 'NO_PARAMS', '_id': item['_id'],'key': item['key'], 'rank': rank, 'category': category}  # 日志用

    def amztracker(self, response):
        self.logger.info(f'amztracker function called on {response.url}')  # 信息会打印在控制台
        item = response.meta['item']
        item['sales']=response.text.strip() # 销量可能为0
        yield item
        if item['sales']=='':
            yield {'url': response.url, 'error': 'NO_SALES', 'rank': item['rank'], 'category': item['category'],'_id': item['_id'], 'key': item['key']}  # 日志用

    def error(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            if response.meta['depth'] < RETRY:
                failure.request.dont_filter = True  # Scrapy默认的DUPEFILTER_CLASS无须加dont_filter=True属性，但如果使用scrapy_redis,则需要手动添加dont_filter属性
                yield failure.request
            else:
                yield {   
                    'url': response.url, 'error': 'HttpError', 'depth': response.meta['depth'],
                    'priority': response.request.priority, 'status': response.status,
                    'callback': response.request.callback.__name__,
                    'key':response.meta.get('key') or response.meta.get('item',{}).get('key',''),
                }   # 日志用          
        elif failure.check(TimeoutError, TCPTimedOutError, ConnectionRefusedError, DNSLookupError):
            request = failure.request
            yield {
                'url': request.url, 
                'error': 'TimeoutError', 
                'priority': request.priority,
                'callback': request.callback.__name__,
                'key':request.meta.get('key') or request.meta.get('item',{}).get('key',''),
            }   # 日志用,只在最后一次超时后才执行
        else:
            request = failure.request
            yield {'url': request.url, 'error': 'UnknownError', 'priority': request.priority,
                   'callback': request.callback.__name__}  # 日志用
