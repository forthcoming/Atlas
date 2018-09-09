import scrapy

class Render(scrapy.Spider):
    name = "render"
    start_urls=['http://quotes.toscrape.com/js/']
    custom_settings={
        # 'DOWNLOAD_DELAY':2,
        'CONCURRENT_REQUESTS':1,
        "DOWNLOADER_MIDDLEWARES":{
            'spider.utils.middlewares.JSRenderMiddleware': 543,
        },
    }

    def parse(self, response):
        for quote in response.css('div.quote'):
            print( {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('span small::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            })
            # print(response.request.headers)
            next_page = response.css("li.next > a::attr(href)").extract_first()
            if next_page:
                yield response.follow(next_page, callback=self.parse,meta={'js':True})
