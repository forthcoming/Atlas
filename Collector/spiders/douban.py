# -*- coding: utf-8 -*-

'''
1.如果在Settings文件中没有指定IMAGES_URLS_FIELD，则默认用image_urls保存图片的地址
2.settings添加'scrapy.pipelines.images.ImagesPipeline':1,或者自定义管道
3.默认使用的image_urls必须是可迭代对象
'''

from scrapy import Spider
from Collector.items import ImageItem
from scrapy.linkextractors import LinkExtractor as LE
from re import compile
import requests

class DoubanSpider(Spider):
  '''
  custom_settings = {
      'ITEM_PIPELINES':{    #不会再调用Settings中的JsonPipeline中间件
          'scrapy.pipelines.images.ImagesPipeline':1,
      },
      'IMAGES_STORE':'photo1',    #没有则新建,已经存在的图片不会再下载
      'IMAGES_URLS_FIELD':'image_urls',
  }
  '''
  
  custom_settings = {
      'ITEM_PIPELINES':{
          'Collector.pipelines.ImagePipeline':1,
      },
      'IMAGES_EXPIRES':90,   #单位是天，调整失效期限，避免下载最近已经下载的图片
      'IMAGES_THUMBS':{
     	  'small':(100,100),
          'big':(500,500),
      }
  }

  name="douban"
  start_urls=('https://movie.douban.com/celebrity/1016930/photos/?start={}'.format(_) for _ in range(0,80,40))

  def parse(self,response):
    #print response.request.headers
    le=LE(restrict_xpaths='//*[@class="poster-col4 clearfix"]',tags='a',attrs='href',) #如何获取img标签的src地址？？？
    urls=le.extract_links(response)
    regex=compile(r'/photo/(\d+)/')
    image_urls=('https://img3.doubanio.com/view/photo/photo/public/p{}.jpg'.format(regex.search(_.url).group(1)) for _ in urls)
    yield ImageItem(image_urls=image_urls,my_image_urls=image_urls,)

    '''
    requests_urls={regex.search(_.url).group(1):'https://img3.doubanio.com/view/photo1/photo1/public/p{}.jpg'.format(regex.search(_.url).group(1)) for _ in urls}
    for key,value in requests_urls.items():
      with open('photo1/{}.jpg'.format(key),'wb') as f:
        f.write(requests.get(value).content)
        #为什么ImagesPipeline下载的图片偏小，而requests跟手动下载图片大小一致
    '''

