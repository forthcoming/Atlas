# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


alih5url = "http://h5api.m.1688.com/h5/mtop.1688.offerservice.getoffers/1.0/?jsv=2.4.11&appKey=12574478&t=1527214611708&sign=da3f8580546c6e9934fbdc6533f773c9&api=mtop.1688.offerService.getOffers&v=1.0&type=jsonp&dataType=jsonp&callback=mtopjsonp1"

alicookie ="ali_apache_id=11.137.166.74.1529406091404.337731.2; UM_distinctid=16417b4f3b21e2-09a1254b7d05a4-3b700558-1fa400-16417b4f3b338d; cna=WcvBD7DRVhMCAT2UyQKF8VNj; ctoken=FSzYZoQnsc5rqVAVHN7tpineneedle; " \
    "EGG_SESS=gDQPK0sUuKcb23a5rakp4Ljziy4IzCTh2vMYtHMA7jNOUxZXroXo88hREQytAbAZFz10T5BFhR_7cFsdnBRYV5EIWXsBFDGOWicaIi9kppMBBNFRd0M3_4FzF0qUGILVu3I43zcRHmllak9eBsXfbg==; " \
    "CNZZDATA1000282329=1309114620-1529493584-%7C1529493584; CNZZDATA1261998348=1007584289-1529496771-%7C1529496771; __cn_logon__=true; __cn_logon__.sig=i6UL1cVhdIpbPPA_02yGiEyKMeZR2hBfnaoYK1CcrF4; " \
    "ali-ss=eyJ1c2VySWQiOm51bGwsImxvZ2luSWQiOm51bGwsInNpZCI6bnVsbCwiZWNvZGUiOm51bGwsIm1lbWJlcklkIjpudWxsLCJrb2EtZmxhc2giOnt9LCJfZXhwaXJlIjoxNTI5NTg2MzE5MDg2LCJfbWF4QWdlIjo4NjQwMDAwMH0=; " \
    "ali-ss.sig=LsIF3RtVoz7X6-KPWb_OkUUwPbf9AXNtRWCU9286Rk0; XSRF-TOKEN=fe78ad92-48a8-43a0-94cb-df1715df8bf6; CNZZDATA1000231236=84677277-1529404287-%7C1529496247; webp=1; isg=BOLiWXsezRebPtCT5qDyCOCtM2GEmw3Nnl9SYyx7DtUA_4J5FMM2XWh9KzsDdF7l; "


aliheaders = {
    "accept": "*/*",
    "scheme": "https",
    "cache-control": "no-cache",
    "proxy-connection": "keep-alive",
    "authority": "h5api.m.1688.com",
    "accept-language": "zh-CN,zh;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "referer": "http://m.1688.com/?src=desktop",
    "User-Agent": ''
}

aliparams = {'proxies': True, 'session': True, 'ua': 'mob', 'timeout': 15}

tbheaders = {
    "accept": "*/*",
    "scheme": "https",
    "proxy-connection": "keep-alive",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "referer": "https://s.taobao.com/list?spm=a21bo.2017.201867-links-0.4.5af911d90wkkOt",
    "User-Agent": "",
}

tbparams = {'proxies': True, 'session': True, 'ua': 'mob', 'timeout': 15}
