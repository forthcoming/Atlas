# coding=utf-8
from pymongo import MongoClient
from hashlib import md5
from datetime import datetime
import os,cx_Oracle
from atlas.config.settings import *

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

def sync():
    client = MongoClient(MONGO_URI)
    db=client[MONGO_BI]
    bi=db['product_bi']
    connection = cx_Oracle.connect(ORACLE_USER, ORACLE_PASSWORD, ORACLE_DWTEST)
    cursor = connection.cursor()
    result=bi.find({},{"dw_etl_dt":1,'_id':0}).sort([('dw_etl_dt',-1)]).limit(1)
    try:
        _last_time=next(result)['dw_etl_dt']
    except:
        _last_time=datetime(1992,8,24)
    last_time="date'{}-{}-{}'".format(_last_time.year,_last_time.month,_last_time.day)
    sql='''
    select 
    id,
    product_name,
    cat_name,
    currency,
    sale_price,
    original_price,
    sale_num,
    comment_count,
    product_url,
    product_image,
    category_id,
    dw_web_id,
    dw_web_name,
    sort_num, 
    sort_type,
    rating,
    praise_cnt,
    collection_cnt,
    score_type,
    score_a,
    dw_sys_dt,
    dw_etl_dt,
    cross_cnt,
    cross_info,
    sort_num_7,
    up_num,
    up_rank,
    sort_num_3,
    data_source,
    ps_product_sn,
    dw_category_name,
    goods_sn
    from dwi.v_dwi_net_product_pool a where a.dw_etl_dt>={} order by a.dw_etl_dt asc'''.format(last_time)
    cursor.execute(sql)
    for each in cursor:
        try:
            sale_price=int(each[4]*100)
        except:
            sale_price=0
        try:
            original_price=int(each[5]*100)
        except:
            original_price=0
        data={
            'product_name':each[1],
            'cat_name':each[2],
            'currency':each[3],
            'sale_price':sale_price,
            'original_price':original_price,
            'sale_num':each[6],
            'comment_count':each[7],
            'product_url':each[8],
            'product_image':[each[9]],
            'category_id':each[10],
            'dw_web_id':each[11],
            'dw_web_name':each[12],
            'sort_num':each[13],
            'sort_type':each[14],
            'rating':each[15],
            'praise_cnt':each[16],
            'collection_cnt':each[17],
            'score_type':each[18],
            'score_a':each[19],
            'dw_sys_dt':each[20],
            'dw_etl_dt':each[21],
            'cross_cnt':each[22],
            'cross_info':each[23],
            'sort_num_7':each[24],
            'up_num':each[25],
            'up_rank':each[26],
            'sort_num_3':each[27],
            'data_source':each[28],
            'ps_product_sn':each[29],
            'dw_category_name':each[30],
            'goods_sn':each[31]
        }
        data['hash_url']=md5(data['product_url'].encode('utf-8')).hexdigest()
        print('processing {}'.format(data['product_url']))
        bi.update_one({"ps_product_sn":data["ps_product_sn"]},{'$setOnInsert': data},upsert=True)
    client.close()

if __name__=='__main__':
    sync()
    # https://oracle.github.io/odpi/doc/installation.html#linux
