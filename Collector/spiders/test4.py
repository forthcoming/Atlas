#coding:utf-8
'''
scrapy-redis核心代码解析
spiders.py和connection.py实现分布式（手动推进去地址）
pipelines.py和connection.py实现把数据存储到redis数据库
scheduler.py，dupefilter.py，queue.py和connection.py实现断点续爬,分布式

需要开启redis-server并安装scrapy-redis
要想实现分布式，只需将该spider复制一份，然后再运行即可
一旦启动了scrapy_redis.pipelines.RedisPipeline,会将item数据保存到dmoz:item中,通过type dmoz:items可得其类型为list
item_key(self, item, spider)此处可以自定义item_key
SCHEDULER_PERSIST = True，中断程序，dmoz:dupefilter和dmoz:requests会存在，程序执行完后还会保存dmoz:dupefilter（此时已不存在dmoz:requests）
SCHEDULER_PERSIST = False，中断程序，dmoz:dupefilter和dmoz:requests会被清空，程序执行完后会删除dmoz:dupefilter（此时已不存在dmoz:requests）
type dmoz:dupefilter返回set
type dmoz:requests返回zset
'''

from scrapy import Request,Spider
from Collector.items import ImageItem

class RedisSpider(Spider):

  custom_settings = {
    'ITEM_PIPELINES':{
    'Collector.pipelines.MyRedisPipeline': 300,   #注意pipeline的先后顺序!!!
    'Collector.pipelines.RedisPipeline': 400,
    #'scrapy_redis.pipelines.RedisPipeline': 400,
    },
    #'SCHEDULER':'scrapy_redis.scheduler.Scheduler', #会产生dmoz:dupefilter和dmoz:requests。如果不启用的话，则调用Scrapy默认的SCHEDULER
    'SCHEDULER':'Collector.utils.scheduler.Scheduler',
    'SCHEDULER_PERSIST':True,
    #'SCHEDULER_QUEUE_CLASS':'scrapy_redis.queue.SpiderStack',
    #'SCHEDULER_QUEUE_CLASS':'scrapy_redis.queue.SpiderQueue',
    #'SCHEDULER_QUEUE_CLASS':'scrapy_redis.queue.SpiderPriorityQueue',
    #'REDIS_HOST':'localhost',
    #'REDIS_PORT':6379,
  }

  name = 'dmoz'
  allowed_domains = ['dmoz.org']
  start_urls = ['http://www.dmoz.org/']


  def parse(self, response):
    for li in response.xpath('//*[@id="catalogs"]//a/@href').extract():
      yield Request(response.urljoin(li),callback=self.parse_item)

  def parse_item(self, response):
    yield ImageItem(url=response.url,)

