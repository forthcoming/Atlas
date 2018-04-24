import requests,re,pymysql,time,random
from datetime import datetime

AGENT=[
    'SAMSUNG-SGH-A867/A867UCHJ3 SHP/VPP/R5 NetFront/35 SMM-MMS/1.2.0 profile/MIDP-2.0 configuration/CLDC-1.1 UP.Link/6.3.0.0.0', 
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7', 
    'Opera/9.20 (Macintosh; Intel Mac OS X; U; en)', 
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER', 
    'SonyEricssonK810i/R1KG Browser/NetFront/3.3 Profile/MIDP-2.0 Configuration/CLDC-1.1', 
]
WEBSITEID=1
topK = 100
DATE = datetime.now().strftime('%Y%m%d%H%M%S')
con = pymysql.connect(
    host='192.168.105.24',
    user='databot',
    password='cuckoo201804',
    db='d_clubfactory',
    charset='utf8mb4',
    use_unicode=True,
)

sess=requests.Session()
sess.headers={
    'accept': '*/*',
    'content-type': 'application/json',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'cookie':'t_uid=c4929da6-ca29-4143-83e9-e996fcac4189;',
}

with con.cursor() as cur:
    cur.execute(
        f'select id,category_url from website_category where website_id={WEBSITEID} and category_url!="" order by id')
    with open('lazada.sql','w',encoding='utf-8') as f:
       for each in cur:
            goods=set()
            index=1
            category_id=each[0]
            start_url=each[1]
            page=1
            sort_type=1
            flag=True
            while flag:
                url=f'{start_url}?ajax=true&page={page}'
                sess.headers['referer']=f'{start_url}?page={page}'

                while True:
                    try:

                        sess.headers['user-agent']=random.choice(AGENT)
                        time.sleep(random.uniform(0,10))
                        r=sess.get(url,timeout=18)
                        items=r.json()['mods']['listItems']
                        if items:
                            print('OK',url,items)
                            for item in items:
                                sku=item.get('cheapest_sku', '')
                                if not (sku in goods):
                                    goods.add(sku)
                                    _={
                                        'product_name': item.get('name', ''),
                                        'sale_price': float(item.get('price',0))/1000,
                                        'original_price': float(item.get('originalPrice',0))/1000,
                                        'comment_count': item.get('review', 0),
                                        'product_url': re.sub(r'^//', '', item.get('productUrl', '')),
                                        'product_image': item.get('image', ''),
                                        'rating': item.get('ratingScore', .0),
                                        'goods_sn':sku,
                                        'website_id': WEBSITEID,
                                        'sort_type': 1,
                                        'image_status': 0,
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
                        
                        break
                    except:
                        print(f'TimeoutError found in {url}!')
