# coding=utf-8
from pymongo import MongoClient
import pymysql,re
from atlas.config.settings import *
from datetime import datetime

db='d_gearbest'
cat_offset=-1050000
web_offset=8
dw_web_name='gearbest'

mysql_con=pymysql.connect(
    host='rm-j6c075x4k8oto805dho.mysql.rds.aliyuncs.com',
    port=3306,
    db=db,
    user='databot',
    password='cuckoo201804',
    charset='utf8mb4',
    use_unicode=True,
)

def sync():
    client=MongoClient(MONGO_URI)
    bi=client[MONGO_BI]
    target=bi['product_bi_final']
    mapping=bi['mapping']

    for each in mapping.find({}, {'bi_cat_id': 1, 'bi_cat_name': 1, '_id': 0, 'erp_cat_id': 1}):
        result = target.find({'category_id': each['bi_cat_id']}, {"updated_time": 1, '_id': 0}).sort([('updated_time', -1)]).limit(1)
        try:
            last_time = next(result)['updated_time']
        except:
            last_time = datetime(1992, 8, 24)
        with mysql_con.cursor() as cur:
            cur.execute('''select 
                updated_time,
                product_url,
                sort_num,
                sort_type,
                sale_price,
                sale_num,
                rating,
                product_name, 
                product_image, 
                original_price,
                website_id as dw_web_id,
                comment_count,
                goods_sn
                from website_product where category_id={} and updated_time>="{}" order by updated_time asc'''.format(each['bi_cat_id']-cat_offset,last_time)
            )
            for item in cur:
                data={
                    'product_url':item[1],
                    'category_id':each['bi_cat_id'],
                    'erp_cat_id':each['erp_cat_id'],
                    'comment_count':int(item[11]),
                    'currency':"¥",
                    "original_price" : 0,
                    'product_image':re.findall(r'https://.+?\.jpg|http://.+?\.jpg',item[8]),
                    'product_name':item[7],
                    'rating':item[6],
                    'sale_num':int(item[5]),
                    'sale_price':int(item[4]*100),
                    'sort_num':item[2],
                    'sort_type':item[3],
                    'updated_time':item[0],
                    'dw_web_name':dw_web_name,
                    'goods_sn':item[12],
                }
                target.update_one({'goods_sn':goods_sn,'dw_web_id':item[10]+web_offset},{'$set':data},upsert=True)
                print('processing {}'.format(data['product_url']))   
                
    client.close()

if __name__=='__main__':
    sync()
    