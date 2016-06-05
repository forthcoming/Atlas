#coding:utf-8
from scrapy import Spider,FormRequest

class Letou360Spider(Spider):
  name='letou360'
  allowed_domains=['letou360.com']
  start_urls=[
    'http://www.letou360.com/invests',
  ]

  def parse(self,response):   
    idt=response.xpath('//div[@class="sabrosus"]/span/a/@id').extract()
    idt+=['form:j_idt112']
    viewstate= response.xpath('//*[@id="javax.faces.ViewState"]/@value').extract()[0]
    for _ in idt:
      data = {
        'form': 'form',
        'javax.faces.ViewState': viewstate,
        'javax.faces.source': _,
        'javax.faces.partial.event': 'click',
        'javax.faces.partial.execute': '{} {}'.format(_,_),
        'javax.faces.partial.render': 'form:showlist',
        'javax.faces.behavior.event': 'action',
        'javax.faces.partial.ajax': 'true',
      }
      yield FormRequest(self.start_urls[0],callback=self.parse_item,meta={'index':_},formdata=data)


  def parse_item(self, response):
    with open('{}.html'.format(response.meta['index']),'w') as f:
      f.write(response.text)
