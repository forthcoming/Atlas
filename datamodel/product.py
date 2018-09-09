import datetime
from atlas.utils.mapping.JsonModelMapping import JsonModelMapping

class Product(JsonModelMapping):
    _id = ''
    system_id = ''
    product_id = ''
    currency = ''
    image = []
    keywords = ''
    platform = ''
    price = 0
    product_url = ''
    sales = 0
    title = ''
    comment = []
    seller_name = ''
    contact = []
    is_hash = False
    ext_price = []


class HistoryProduct(JsonModelMapping):
    category = ''
    keywords = ''
    system_id = ''
    price = 0
    inventory = []
    seller_name = ''
    record_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")