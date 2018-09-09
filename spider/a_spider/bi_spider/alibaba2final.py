# coding=utf-8
from pymongo import MongoClient
import pymysql,re
from atlas.config.settings import *
from hashlib import md5
from datetime import datetime

mysql_con=pymysql.connect(
    # host='192.168.105.24',
    host='14.21.46.234',
    port=61106,
    user='databot',
    password='cuckoo201804',
    db='d_alibaba',
    charset='utf8mb4',
    use_unicode=True,
)
OFFSET=5000

def sync():
    client=MongoClient(MONGO_URI)
    bi=client[MONGO_BI]
    target=bi['product_bi_final']
    category=bi['category']
    
    for each in category.find({'dw_web_id':2},{'category_id':1,'dw_category_name':1,'_id':0}):
        result=target.find({'category_id':each['category_id']},{"updated_time":1,'_id':0}).sort([('updated_time',-1)]).limit(1)
        try:
            last_time=next(result)['updated_time']
        except:
            last_time=datetime(1992,8,24)

        with mysql_con.cursor() as cur:
            cur.execute('''select 
                category_id,
                product_url,
                sort_num,
                sort_type,
                atlas_price as sale_price,
                sale_num,
                rating,
                product_name, 
                product_image, 
                original_price,
                website_id as dw_web_id,
                comment_count,
                goods_sn,
                updated_time
                from website_product_copy where category_id={} and updated_time>="{}" order by updated_time asc'''.format(each['category_id']-OFFSET,last_time)
            )
            for item in cur:
                try:
                    comment_count=int(item[11])
                except:
                    comment_count=0
                try:
                    _sale_num=item[5]
                    if u'万' in _sale_num:
                        sale_num=int(float(re.findall(r'\d+\.\d+',_sale_num)[0])*10000)
                    else:
                        sale_num=int(_sale_num)
                except Exception:
                    sale_num=0
    
                data={
                    'product_url':item[1],
                    'category_id':item[0]+OFFSET,
                    'comment_count':comment_count,
                    'currency':"¥",
                    'dw_web_id':item[10],
                    # 'original_price':item[9],
                    "original_price" : 0,
                    'product_image':re.findall(r'https://.+?\.jpg|http://.+?\.jpg',item[8]),
                    'product_name':item[7],
                    'rating':item[6],
                    'sale_num':sale_num,
                    'sale_price':item[4],
                    'sort_num':item[2],
                    'sort_type':item[3],
                    'updated_time':item[13],
                    "supplier_num" : 0,
                    "min_price" : 0,
                    "max_price" : 0,
                    "cross_info" : None,
                    "ps_product_sn" : "",
                    'dw_etl_dt':datetime(1992,8,24),
                    "data_source" : 0,
                    "score_a" : 0,
                    "sort_num_3" : None,
                    "sort_num_7" : None,
                    "cross_cnt" : None,
                    "dw_sys_dt" : datetime(1992,8,24),
                    "up_num" : None,
                    "up_rank" : None,
                    "collection_cnt" : 0,
                    "praise_cnt" : 0,
                    'dw_web_name':'1688中国站',
                    "cat_name" : "",       # 弃用
                    'dw_category_name':each['dw_category_name']  # 待弃用
                }
                data['hash_url']=md5(data['product_url']).hexdigest()   # py2
                # data['hash_url']=md5(data['product_url'].encode('utf-8')).hexdigest()   # py3
                target.update_one({'goods_sn':item[12],'dw_web_id':data['dw_web_id']},{'$set':data},upsert=True)
                print('processing {}'.format(data['product_url']))   
                
    client.close()

if __name__=='__main__':
    sync()
