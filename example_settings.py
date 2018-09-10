# coding=utf-8
from os import path

# 当MONGO_URI = mongodb://{ip}:{port} 为无密码模式  mongodb://{user}:{password}@{ip}:{port} 为用户密码登录模式
# MONGO_{} = 数据库名 MONGO_SET = 固定的集合名
MONGO_URI = "mongodb://192.168.105.20:27017"
MONGO_ATLAS = "atlas_test"
MONGO_BI = "Atlas_BI"
MONGO_SET = "category_info"

# [proxy]
PROXY_HOST = "p10.t.16yun.cn"
PROXY_PORT = "6446"
PROXY_USER = "********"
PROXY_PASS = "123456"

# 当PRODUCT_SUM = string类型时，抓取数量为无限大， 为int时可限制抓取数量
# [Offset]
PRODUCT_SUM = '∞'

# [mysql]
MYSQL_HOST = "192.168.105.238"
MYSQL_USER = "erp"
MYSQL_PASSWORD = "erp123456"
MYSQL_PRODUCT = "product"

# 邮箱配置
SP_MAIL_ADDRESS = 'itnotitfysercices@qq.com'
SP_MAIL_SENDER = 'Asoulwangxiaohei'
SP_MAIL_SMTP = 'smtp.qiye.163.com'
SP_MAIL_SMTP_PORT = '465'
SP_MAIL_LOGINNAME = 'itnotitfysercices@qq.com'
SP_MAIL_PASSWORD = 'Love2017!'

# 路由分发
MACHINE_ID='atlas_192.168.105.20'

# [oracle]
ORACLE_USER = "erp"
ORACLE_PASSWORD = "erp123456"
ORACLE_DWTEST = "192.168.105.106/dwtest"

# image
OFFSET=(1<<6)-1
PATH='/'.join(path.realpath(__file__).split('/')[:-3])+'/image/'
