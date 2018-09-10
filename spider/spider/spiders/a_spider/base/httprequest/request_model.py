import sys
import time
import Queue
import random
# import logging
import requests
import linecache
import threading
from multiprocessing import Value
# from atlas.log.log import Log
from atlas.config.settings import *
from atlas.utils.request_tools.request_tool import *
reload(sys)
sys.setdefaultencoding('utf-8')
'''
使用方法：
    导入本代码，创建CuckooHttpRequest()类对象
    如：cuc_req = CuckooHttpRequest()
    使用get方法或post方法 （目前只支持这两种请求模式）
        cuc_req.get()

与第三方requests库的功能差异：
    参数proxies接受True值，默认为None（不使用代理），当值为True时将自动读取配置文件中的代理信息。
    新植入参数session，接受True，默认为None（不使用session），当值为True时将自动以session模式请求链接。
    新植入参数ua，接受"pc"或"mob"，默认为None（不使用User-Agent）；
    当值为"pc"时，自动随机挂载电脑端ua，当值为"mob"时，自动随机挂载移动端ua。
        注意：
            当传入自定义headers时，如果不使用ua参数，则默认使用headers中的User-Agent。
            当传入自定义headers，同时使用ua参数，则根据ua的值覆盖原headers中的User-Agent。
            也可在不传入headers时使用ua参数，会默认挂载以"User-Agent"作为键，传入请求中。（适合在编写代码时的快速测试）

'''
mutex = threading.Lock()
atomValue = Value('l', 0)


def interval_delay():
    mutex.acquire()
    time.sleep(0.1)
    mutex.release()
    atomValue.value += 1


# @Log(level=logging.INFO,name='req.log')
class CuckooHttpRequest(object):
    def __init__(self):
        # 代理服务器
        proxy_host = PROXY_HOST
        proxy_port = PROXY_PORT

        # 代理隧道验证信息
        proxy_user = PROXY_USER
        proxy_pass = PROXY_PASS

        proxy_meta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxy_host,
            "port": proxy_port,
            "user": proxy_user,
            "pass": proxy_pass,
        }
        print '[INFO]: proxy：', proxy_meta
        self.proxy = {
            "http": proxy_meta,
            "https": proxy_meta,
        }

        self.s_requests = requests.session()
        self.data_queue = Queue.Queue()
        self.startTime = time.time()
        self.cookies = ""
        self.headers = {}
        self.iswubai = 0

    def get(self, url, ua=None, session=None, params=None, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request_func('get', url, ua=ua, session=session, params=params, **kwargs)

    def post(self, url, ua=None, session=None, data=None, json=None, **kwargs):
        return self.request_func('post', url, ua=ua, session=session, data=data, json=json, **kwargs)

    @staticmethod
    def change_ua(ua='pc'):
        tunnel = random.randint(1, 998)
        if ua == 'pc':
            ua_file = '1000ua-pc.txt'
        elif ua == 'mob':
            ua_file = '1000ua-android.txt'
        else:
            return None
        user_agent = linecache.getline(ua_file, tunnel)
        # print user_agent
        return user_agent.strip().replace('\n', '').replace('\r', '')

    def headers(self):
        # 马云下网站请求头携带Host会导致无法访问数据
        header = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # "Cookie": 'ctoken=CNYRTQcjjRJf8PYdFfxUnaga; __cn_logon__=false; ali-ss=eyJ1c2VySWQiOm51bGwsImxvZ2l
            # uSWQiOm51bGwsInNpZCI6bnVsbCwiZWNvZGUiOm51bGwsIm1lbWJlcklkIjpudWxsLCJfZXhwaXJlIjoxNTI3MzAzNjAzMzc0L
            # CJfbWF4QWdlIjo4NjQwMDAwMH0=; UM_distinctid=163953d2a022be-0ada2a3e62f6b4-2d604637-4a640-163953d2a0
            # 3e96; cna=WcvBD7DRVhMCAT2UyQKF8VNj; webp=1; _m_h5_tk=f717234e6323b40456877cd1ef1ddcc9_152721968342
            # 6; _m_h5_tk_enc=72a92d87807fcd12f4c75b9a1192f061; isg=BNTUvIwuc4Bp1eY5pO7cgkKLpRuGhcOXja66U261Yd_i
            # WXWjlj1Pp5KXXVdBoTBv',
            # "Host": "h5api.m.1688.com",
            "Pragma": "no-cache",
            "Referer": "http://m.1688.com/?src=desktop",
            # "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML,
            #  like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
            'User-Agent': self.change_ua(),
        }
        return header

    def request_func(self, method, url, ua=None, session=None, params=None, data=None, json=None, **kwargs):

        kwargs['proxies'] = self.proxy if 'proxies' in kwargs.keys() else {}
        resquests_model = requests if not session else self.s_requests
        if 'headers' in kwargs.keys() and (ua == "pc" or ua == "mob"):
            if 'User-Agent' in kwargs['headers'].keys():
                kwargs['headers']['User-Agent'] = self.change_ua(ua=ua)
            elif 'user-Agent' in kwargs['headers'].keys():
                kwargs['headers']['user-Agent'] = self.change_ua(ua=ua)
            elif 'user-agent' in kwargs['headers'].keys():
                kwargs['headers']['user-agent'] = self.change_ua(ua=ua)
            elif 'User-agent' in kwargs['headers'].keys():
                kwargs['headers']['User-agent'] = self.change_ua(ua=ua)
            else:
                raise Exception("请在请求头中添加ua的键值，如“ 'User-Agent': '' ”")

        elif 'headers' not in kwargs.keys() and (ua == "pc" or ua == "mob"):
            _ua = {'User-Agent': self.change_ua(ua=ua)}
            kwargs['headers'] = _ua

        # print '[INFO]: 正在请求：', url
        interval_delay()
        print "[INFO]: Seconds: {}, Request_Count: {} ".format(time.time() - self.startTime, atomValue.value)
        return resquests_model.get(url, params=params, **kwargs) if method == "get" \
            else resquests_model.post(url, data=data, json=json, **kwargs)
