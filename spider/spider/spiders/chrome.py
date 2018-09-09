from selenium import webdriver
from pydispatch import dispatcher
from scrapy import signals,Spider,Selector
from selenium.common.exceptions import NoSuchElementException
from spider.settings import *

class Chrome(Spider):
    name = "chrome"
    start_urls = [
        'http://quotes.toscrape.com/js-onclick',
    ]
    custom_settings={
        # 'DOWNLOAD_DELAY':2,
        # 'CONCURRENT_REQUESTS':10,
    }

    def __init__(self):
        dispatcher.connect(self.spider_closed,signals.spider_closed)
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')  # 只针对非headless模式的root用户
        options.add_argument(f'--user-data-dir={CHROME_DATA}')
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(chrome_options=options,executable_path='/opt/google/chrome/chromedriver')    

    def parse(self, response):
        self.driver.get(response.url)
        while True:
            sel = Selector(text=self.driver.page_source)
            for quote in sel.css('div.quote'):
                print({
                    'text': quote.css('span.text::text').extract_first(),
                    'author': quote.css('span small::text').extract_first(),
                    'tags': quote.css('div.tags a.tag::text').extract(),
                })
            try:
                next_button = self.driver.find_element_by_css_selector('li.next > a')
                next_button.click()
            except NoSuchElementException:
                break
    
    def spider_closed(self):
        self.driver.quit()
    