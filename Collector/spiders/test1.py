#coding:utf-8
from scrapy import Spider
from scrapy.selector import Selector
from Collector.items import OilItem

class Test1Spider(Spider):
  name='test1'
  start_urls=[
    "http://pdcmt.pconline.com.cn/front/mtp-list.jsp?productId=554672&filterBy=-1&itemCfgId=-1&order=2&pageNo=4",
    "http://product.pcpop.com/AjaxDataOperate/ProductComment.aspx?CurrentPage=2&F_ProductSN=000344893&F_SeriesSN=&F_BrandSN=01334",
    "http://detail.zol.com.cn/xhr3_Review_GetListAndPage_isFilter=0%5EproId=392008%5Epage=4.html",
  ]
  def parse(self,response):
    
    if 'pconline' in response.url:
      for i in response.xpath('//div[@class="contentdiv"]/ul/li'):
        _=i.xpath('./div[1]/dl[1]/dd/text()').extract()
        if _:
          print(_[0])
          print(type(_[0]))     #str
          yield OilItem(placeName=_[0])
      #print(response.body.decode('gbk'))          #正常显示
      #print(response.text)                        #正常显示
      print(type(response.body))                  #bytes
      print(type(response.body.decode('gbk')))    #str
      print(type(response.text))                   #str

    '''
    if 'pcpop' in response.url:
      for i in response.xpath('//*[@id="proComList"]/li'):
        _=i.xpath('./div[@class="title"]/b/a/text()').extract()[0]
        print(_)
        yield OilItem(placeName=_)
      print('\n---------\n',Selector(text=response.text),'\n---------\n')

    if 'xhr3_Review_GetListAndPage_isFilter' in response.url:
      #have to use Selector,or you will get none
      sel=Selector(text=response.body.decode('unicode_escape').replace('\/','/'))
      for i in sel.xpath('//ul[@class="comment-list"]/li'):
        _=i.xpath('./div[@class="comments-list-content"]/div[@class="comments-content"]/h3/a/text()').extract()[0]
        yield OilItem(placeName=_)
      #print(response.body.decode('unicode_escape'))       #正常显示
    '''
