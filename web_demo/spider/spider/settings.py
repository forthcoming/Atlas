# -*- coding: utf-8 -*-
from os import path

BOT_NAME = 'spider'
SPIDER_MODULES = ['spider.spiders']
NEWSPIDER_MODULE = 'spider.spiders'
ITEM_PIPELINES = {
    'spider.pipelines.JsonPipeline': 300,
}
DOWNLOADER_MIDDLEWARES = {
    'tools.middlewares.HeadersMiddleware': 543,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}
COOKIES_ENABLED=True    # Default True,If disabled, no cookies will be sent to web servers.
#当启用HeadersMiddleware时将无视USER_AGENT设置
USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36'
ROBOTSTXT_OBEY = False
DATAPATH=f'{path.split(__file__)[0]}/../data/'
CHROME_DATA=f'{path.split(__file__)[0]}/../chrome/'   

# LOG_ENABLED = True   #default True
# LOG_ENCODING = "utf-8"
# LOG_FILE = "log/spider.log"
# LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
# LOG_DATEFORMAT = "%Y-%m-%d %H:%M:%S"
# LOG_LEVEL = 'DEBUG'
# LOG_STDOUT=False #default false,If True, all standard output (and error) of your process will be redirected to the log
# DUPEFILTER_CLASS = 'tools.middlewares.MyRFPDupeFilter'



print(f'{path.split(__file__)[0]}/data/')