#coding:utf-8
from scrapy import Spider
from scrapy.selector import Selector
from selenium import webdriver

class SeleniumSpider(Spider):
  name = "selenium"
  start_urls=['http://flights.ctrip.com/booking/sha-bjs---d-adu-1/?ddate1=2015-11-18&ddate2=2015-11-19',]

  def parse(self,response):
    #driver=webdriver.Firefox()
    driver = webdriver.PhantomJS()
    driver.get(response.url)
    sel=Selector(text=driver.page_source)
    #print(self.driver.page_source)
    #print(self.driver.find_element_by_id("name"))
    _=sel.xpath('string(//*[@id="J_flightlist2"]/div[@id="flight_HO1251"])').extract()[0]
    print(''.join(_.split()))
    driver.quit()
