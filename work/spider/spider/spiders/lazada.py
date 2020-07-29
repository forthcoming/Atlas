from scrapy.spiders import Spider
import json, re, pymysql,time,random
from datetime import datetime
from selenium import webdriver
from spider.settings import *

topK = 100
DATE = datetime.now().strftime('%Y%m%d%H%M%S')

class Lazada(Spider):
    name = "lazada"
    allowed_domains = ['lazada.co.id']
    start_urls=['https://www.lazada.co.id']
    custom_settings={

        'DOWNLOADER_MIDDLEWARES': {
            'tools.middlewares.ProxiesMiddleware': 400,
        },
        'ITEM_PIPELINES': {
            # 'spider.pipelines.MongoPipeline': 299,  #该pipeline优先级应大于Sqlpipeline
            'spider.pipelines.SqlPipeline': 300,
        },
    }

    def parse(self,response):

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1800,1000')
        options.add_argument('--proxy-server=http://127.0.0.1:6789')
        options.add_argument(f'--user-data-dir={CHROME_DATA}')
        options.add_argument('--blink-settings=imagesEnabled=false')
        driver = webdriver.Chrome(chrome_options=options,executable_path='/opt/chromedriver')

        con = pymysql.connect(
            host='192.168.105.24',
            user='databot',
            password='******',
            db='d_lazada',
            charset='utf8mb4',
            use_unicode=True,
        )

        with con.cursor() as cur:
            cur.execute(f'select id,category_url from website_category where website_id=1 and category_url!="" order by id')
            with open(f'lazada{DATE}.sql','w',encoding='utf-8') as f:
               for each in cur:
               #for each in cur.fetchall()[:5]:  # testing!!!
                    goods=set()
                    index=1
                    category_id=each[0]
                    start_url=each[1]
                    page=1
                    flag=True
                    while flag and page<15:  # 个别品类数据量达不到topK,所以要用page限制
                        url=f'{start_url}?page={page}'
                        time.sleep(random.uniform(0,2))

                        while True:
                            try:
                                driver.get(url)
                                break
                            except Exception:
                                driver.quit()
                                driver = webdriver.Chrome(chrome_options=options,executable_path='/opt/chromedriver')

                        #driver.save_screenshot(f"{''.join(url.split('/')[-2:])}.png")  
                        items=re.findall(r'"listItems":(.+)?,"breadcrumb":',driver.page_source)
                        if items:
                            print('OK',url,json.loads(items[0]))
                            for item in json.loads(items[0]):
                                sku=item.get('cheapest_sku', '')
                                if not (sku in goods):
                                    goods.add(sku)
                                    _={
                                        'product_name': item.get('name', '').replace('\\',''),
                                        'sale_price': float(item.get('price',0))/1000,
                                        'original_price': float(item.get('originalPrice',0))/1000,
                                        'comment_count': item.get('review', 0),
                                        'product_url': re.sub(r'^//', '', item.get('productUrl', '')),
                                        'product_image': item.get('image', ''),
                                        'rating': item.get('ratingScore', .0),
                                        'goods_sn':sku,
                                        'category_id': category_id,
                                        'sort_num': index,
                                        'created_time': DATE,
                                    }
                                    fields = ','.join(_.keys())
                                    values = '","'.join(str(each).replace('"','').replace(';','') for each in _.values())
                                    sql = f'insert into website_product({fields}) values("{values}");\n'
                                    f.write(sql)
                                    index+=1
                                    if index>topK:
                                        flag=False
                                        break
                            page+=1
        driver.quit()

