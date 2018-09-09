import pymysql
from pymongo import MongoClient
from atlas.config.settings import *
from atlas.database.atlasDatabase import AtlasDatabase
from atlas.datamodel.product import Product

# mysql_con=pymysql.connect(
#     host='192.168.105.238',
#     user='erp',
#     password='erp123456',
#     db='product',
#     charset='utf8mb4',
#     use_unicode=True,
# )

mysql_con=pymysql.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    db=MYSQL_PRODUCT,
    charset='utf8mb4',
    use_unicode=True,
)

mongo_con=MongoClient(MONGO_URI)
mongo_database=MONGO_ATLAS

def get_leaf(root_id):
    result=[]
    def _get_leaf(parent_id):
        with mysql_con.cursor() as cur:
            cur.execute('select id,leaf from category where parent_id={}'.format(parent_id))
            for each in cur:
                parent_id,leaf=each
                if leaf:
                    result.append(parent_id)
                else:
                    _get_leaf(parent_id)
    _get_leaf(root_id)
    return result

def sync():
    src=AtlasDatabase(MONGO_URI,MONGO_ATLAS)
    db=mongo_con[mongo_database]
    with mysql_con.cursor() as cur:
        for category in db['category_info'].find({'sub_category.platform':'cuckoo','sub_category.source':'erp'},{'name_en':1,'_id':0,'sub_category.$.keyword':1}):
            root_id,name_en=category['sub_category'][0]['keyword'],category['name_en']
            keywords=get_leaf(root_id)
            if keywords:
                cur.execute('select id as product_id,category_id as keywords,title,main_image_url,purchase_price,source_url from product where category_id in ({})'.format(str(keywords)[1:-1]))
                for item in cur:
                # for item in cur.fetchall()[:1]: # testing
                    data=Product()
                    _price=item[4]
                    data.image=['http://pixiu.stosz.com:8900/{}'.format(item[3])]
                    data.product_url=item[5]
                    data.keywords=item[1]
                    data.product_id=item[0]
                    data.title=item[2]
                    data.platform='cuckoo'
                    data.is_hash=False
                    data.price=0 if _price is None else int(_price*100)
                    data.system_id='cuckoo_{}'.format(item[0])
                    if data.product_url and item[3]:
                        src.insertOrUpdateProduct(name_en,data)
                        print('processing {}'.format(item[1]))

if __name__=="__main__":
    sync()
