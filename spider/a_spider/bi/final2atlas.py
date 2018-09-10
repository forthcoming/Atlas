# coding=utf-8
from pymongo import MongoClient
from atlas.config.settings import MONGO_URI,MONGO_BI,MONGO_ATLAS

def get_children(bi,cat_id):
    result=set()
    def _get_children(bi,cat_id):
        result.add(cat_id)
        for each in bi['category'].find({'parent_id':cat_id},{'category_id':1,'_id':0}):
            _get_children(bi,each['category_id'])
    _get_children(bi,cat_id)
    return result

def bi2atlas():
    client=MongoClient(MONGO_URI)
    bi=client[MONGO_BI]
    atlas=client[MONGO_ATLAS]    
    source=bi['product_bi_final']
    website=bi['website']
    mapping=bi['bi_map_erp']
    for outer in atlas['category_info'].find({'sub_category.source':'bi'},{'name_en':1,'_id':0,'sub_category.$.keyword':1}):
        target=atlas['product_{}'.format(outer['name_en'])]
        erp_cat_id=outer['sub_category'][0]['keyword']
        for bi_cat_id in mapping.find({'erp_cat_id':erp_cat_id},{'bi_cat_id':1,'_id':0}):
            for category_id in get_children(bi,bi_cat_id['bi_cat_id']):
                for each in source.find({'category_id':category_id,'goods_sn':{'$exists':True}}):
                    data={
                        'image':each['product_image'],
                        'sales':each['sale_num'],
                        'product_url':each['product_url'],
                        'currency':each['currency'],
                        'keywords':erp_cat_id,
                        'product_id':each['goods_sn'],
                        'title':each['product_name'],
                        'price':each['sale_price'],
                        'platform':website.find_one({'web_id':each['dw_web_id']},{'platform':1,'_id':0})['platform'],
                        'source':'bi',
                        'comment':[],
                        'seller_name':'',
                    }
                    data['system_id']='{}_{}'.format(data['platform'],data['product_id'])
                    print('processing {}'.format(data['product_id']))
                    target.update_one({'system_id':data['system_id']},{'$set':data},upsert=True)

if __name__=='__main__':
    bi2atlas()
