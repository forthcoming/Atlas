# -*- coding: utf-8 -*-
from scrapy import Spider,FormRequest
import json
from Collector.items import JobItem

class LagouSpider(Spider):
  name="lagou"
  pn=1
  allowed_domains=["lagou.com"]
  start_urls=[
             'http://www.lagou.com/jobs/positionAjax.json?px=new',
             ]

  def parse(self,response):

    content=json.loads(response.text).get('content',{}).get('positionResult',{}).get('result',[])
    if(content):
      item=JobItem()
      self.pn+=1
      for _ in content:
        item['leaderName']=_.get('leaderName','None')
        item['companySize']=_.get('companySize','None')
        item['workYear']=_.get('workYear','None')
        item['education']=_.get('education','None')
        item['financeStage']=_.get('financeStage','None')
        item['pvScore']=_.get('pvScore','None')
        item['city']=_.get('city','None')
        item['companyLogo']=_.get('companyLogo','None')
        item['companyId']=_.get('companyId','None')
        item['industryField']=_.get('industryField','None')
        item['companyLabelList']=_.get('companyLabelList','None')
        item['formatCreateTime']=_.get('formatCreateTime','None')
        item['salary']=_.get('salary','None')
        item['positionName']=_.get('positionName','None')
        item['companyName']=_.get('companyName','None')
        item['jobNature']=_.get('jobNature','None')
        item['positionFirstType']=_.get('positionFirstType','None')
        item['createTime']=_.get('createTime','None')
        item['positionId']=_.get('positionId','None')
        item['companyShortName']=_.get('companyShortName','None')
        item['positionType']=_.get('positionType','None')
        item['positionAdvantage']=_.get('positionAdvantage','None')
        yield item
      
      data={
           'first':'false',
           'pn':str(self.pn),
           'kd':'',     
           }
      yield FormRequest(self.start_urls[0],formdata=data)  #默认调用parse,这里不能使用Request
