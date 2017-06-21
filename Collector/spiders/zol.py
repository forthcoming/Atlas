#coding:utf-8
import re
from scrapy import Request
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor as LE
from scrapy.spiders import CrawlSpider, Rule
from Collector.items import PhoneItem

class ZOlSpider(CrawlSpider):
  name = 'zol'
  allowed_domains = ['zol.com.cn']

  # 由于zol调皮了，所以请求时得添加cookies信息和头信息，才给访问哦
  def start_requests(self):
    urls=['http://detail.zol.com.cn/index.php?c=SearchList&subcateId=57&keyword=vivo']
    cookie = {
      'listSubcateId': '57',
      'visited_serachKw': 'vivo',
    }
    head = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36',
    }
    for url in urls:
      yield Request(url, cookies=cookie, dont_filter=True, headers=head)

  def process_value(value):   #注意位置
     print(re.sub(r'page','AVATAR',value))
     return value  #只能是return

  rules = [
          Rule(
               LE(
                 tags=('a'),  #只在本rule下生效
                 attrs=('href',),
                 restrict_xpaths='//div[@class="page"]',
                 canonicalize=False, #去掉#等并把提交数据名按名称排序等
                 process_value=process_value,   # for testing !!!
                 #process_value=lambda x:x+'###',
                 deny='isFilter',
                 #过滤评论中的每一页，大大减少depth，请求数等，提高效率
                 #这也说明在第二条rule中请求的页面也可以被本rule使用
                 ),
               #callback='parse_item',
               follow=True,
               ),
          Rule(
               LE(allow='/\d+/\d+/review\.shtml'),
               callback='parse_item'
              ),
          ]

  def parse_item(self, response):
    sel=Selector(text=response.body.decode('unicode_escape').replace('\/','/'))  # 这一步不能少
    regex=re.compile(r'(?<=/)\d+(?=/review\.shtml)|(?<=proId=)\d+')    #注意这里断言的用法
    proID=regex.search(response.url).group()
    for url in sel.xpath('//div[@class="comments-content"]/h3/a/@href').extract(): #路径最好不要写相对位置如div[3]等
      yield Request(response.urljoin(url),callback=self.parse_comment,meta={'proID':proID})

    next_page=sel.xpath('//div[@class="page"]/a[last()]/@href').extract()
    if next_page:
      num=re.search(r'page=(\d*)',next_page[0]).group(1)
      print(num,response.url)
      #order=1代表综合排序,order=2代表最新发布,默认是1
      next_page='http://detail.zol.com.cn/xhr3_Review_GetListAndPage_order=1%5EisFilter=1%5EproId={}%5Epage={}.html'.format(proID,num)
      yield Request(next_page,callback=self.parse_item)

  def parse_comment(self,response):

    xp=lambda s:response.xpath(s).extract()
    name=xp('(//div[@class="breadcrumb"]/a)[4]/text()')[0]   #注意括号
    evaluation=re.sub(r'\s','',xp('string(//div[@class="comments-content"])')[0]) #注意\s用法
    score=xp('//ul[@class="score-item clearfix"]/li/span[2]/text()')
    integration=xp('(//div[@class="comments-score clearfix"]/div)[1]/strong/text()')
    item=PhoneItem(url=response.url,product_id=response.meta['proID'])
    item['product_name'],item['product_type']=name.split(' ',1) #分割1次
    item['series']=re.search(r' ([a-zA-Z]+)',name).group(1)   #注意要通用,是group(1)
    item['customer_id']=xp('//div[@class="comments-user-name"]//a/text()')[0]
    item['publish_date']=evaluation[:10]
    item['evaluation']=evaluation[10:]
    item['integration_valuation_score']=integration[0] if integration else ''
    (
     item['battery_score'],
     item['screen_score'],
     item['photo_score'],
     item['video_entertainment_score'],
     item['appearance_score'],
     item['cost_performance_score'],
    )=score if score else ('','','','','','')
    yield item
