from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process=CrawlerProcess(get_project_settings())
for spider in ('weibo','zol','zol_plus','pcpop'):
  process.crawl(spider)
process.start()


'''
from scrapy import cmdline
cmdline.execute('scrapy crawl weibo'.split())
'''
