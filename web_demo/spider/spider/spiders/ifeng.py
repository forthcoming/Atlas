#coding:utf-8
'''
start_urls的depth=0
response=response.replace(body=response.body.replace('<em>',''))
如果出现标签套标签，也是一种解决方案
'''
from scrapy import Spider
from pydispatch import dispatcher
from spider.items import OilItemLoader
from scrapy import signals

class Ifeng(Spider):
  count=0
  name='ifeng'
  allowed_domains=['ifeng.com']
  start_urls=[
    'http://app.finance.ifeng.com/data/indu/cpjg.php?symbol=285&kind=塔皮斯现货价格',
    'http://app.finance.ifeng.com/data/indu/cpjg.php?symbol=285&kind=布伦特现货价格',
  ]

  custom_settings={   #覆盖Settings已有的设置
    'DOWNLOAD_DELAY':5,
    'USER_AGENT':'use my customed UserAgent'

  }

  def __init__(self, name=None, **kwargs):
    super(Ifeng, self).__init__(name=name, **kwargs)
    dispatcher.connect(self.item_scraped, signals.item_scraped)

  def item_scraped(self):
    self.count+= 1
    print(self.count)

  def parse(self,response):
    print(response.request.headers['User-Agent'])
    for index,sel in enumerate(response.xpath('//table/tr')[1:3]):
      l=OilItemLoader(selector=sel) #省去了item=OilItem()和response=response
      l.add_xpath('key_name','//title/text()')
      l.add_value('key_name','AKATSUKI')
      l.add_xpath('price_y','td[2]/text()')
      l.add_value('s_remark','')
      l.add_value('s_type','crude')  #此处不用转码
      yield l.load_item()
      self.crawler.stats.inc_value('my_item_count')
      #self.crawler.stats.set_value('hostname', socket.gethostname())
      #self.crawler.stats.max_value('max_items_scraped', value)   #当新的值比原来的值大时设置数据
      #self.crawler.stats.min_value('min_free_memory_percent', value)
      #self.crawler.stats.get_value('pages_crawled')
      #self.crawler.stats.get_stats()    #获取所有数据(爬虫执行完后打印的字典),set_stats,clear_stats
