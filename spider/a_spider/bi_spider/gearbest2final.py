# coding=utf-8
from pymongo import MongoClient
import pymysql,re
from atlas.config.settings import *
from hashlib import md5
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
    idList = []

    with mysql_con.cursor() as cur:
        strSQL = 'select distinct(category_id) from website_product'
        cur.execute(strSQL)

        for item in cur:
            idList.append(item[0] + cat_offset)

    for each in mapping.find({"bi_cat_id": {"$in": idList}},
                             {'bi_cat_id': 1, 'bi_cat_name': 1, '_id': 0, 'erp_cat_id': 1}):
        result = target.find({'category_id': each['bi_cat_id']}, {"updated_time": 1, '_id': 0}).sort(
            [('updated_time', -1)]).limit(1)
        try:
            last_time = next(result)['updated_time']
        except:
            last_time = datetime(1992, 8, 24)
        erp_cat_id = each['erp_cat_id']

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
                try:
                    comment_count=int(item[11])
                except:
                    comment_count=0
                try:
                    sale_num=int(item[5])
                except:
                    sale_num=0
                try:
                    sale_price=int(item[4]*100)
                except:
                    sale_price=0    
                data={
                    'product_url':item[1],
                    'category_id':each['bi_cat_id'],
                    'erp_cat_id':erp_cat_id,
                    'comment_count':comment_count,
                    'currency':"¥",
                    # 'original_price':item[9],
                    "original_price" : 0,
                    'product_image':re.findall(r'https://.+?\.jpg|http://.+?\.jpg',item[8]),
                    'product_name':item[7],
                    'rating':item[6],
                    'sale_num':sale_num,
                    'sale_price':sale_price,
                    'sort_num':item[2],
                    'sort_type':item[3],
                    'updated_time':item[0],
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
                    'dw_web_name':dw_web_name,
                    "cat_name" : "",       # 弃用
                    'dw_category_name':each['bi_cat_name'],  # 待弃用
                    'is_select': 0
                }
                data['hash_url']=md5(data['product_url'].encode('utf-8')).hexdigest()   # py3
                goods_sn=item[12] or data['hash_url']
                target.update_one({'goods_sn':goods_sn,'dw_web_id':item[10]+web_offset},{'$set':data},upsert=True)
                print('processing {}'.format(data['product_url']))   
                
    client.close()

if __name__=='__main__':
    sync()
    