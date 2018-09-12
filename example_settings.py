# coding=utf-8
from os import path

# 当MONGO_URI = mongodb://{ip}:{port} 为无密码模式  mongodb://{user}:{password}@{ip}:{port} 为用户密码登录模式
MONGO_URI = "mongodb://192.168.105.20:27017"
MONGO_ATLAS = "atlas_test"

# [proxy]
PROXY_HOST = "p10.t.16yun.cn"
PROXY_PORT = "6446"
PROXY_USER = "********"
PROXY_PASS = "123456"

# [mysql]
MYSQL_HOST = "192.168.105.238"
MYSQL_USER = "erp"
MYSQL_PASSWORD = "erp123456"
MYSQL_PRODUCT = "product"

# 路由分发
MACHINE_ID='atlas_192.168.105.20'

# [oracle]
ORACLE_USER = "erp"
ORACLE_PASSWORD = "erp123456"
ORACLE_DWTEST = "192.168.105.106/dwtest"

# image
OFFSET=(1<<6)-1
PATH='/'.join(path.realpath(__file__).split('/')[:-3])+'/image/'
