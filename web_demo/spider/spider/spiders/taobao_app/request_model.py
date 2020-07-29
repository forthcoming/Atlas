import time
import Queue
import random
import requests
import linecache
import threading
from multiprocessing import Value
from settings import *
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
mutex = threading.Lock()  # 互斥锁，用来协调0.1秒发送请求
atomValue = Value('l', 0)


def interval_delay():
    mutex.acquire()
    time.sleep(0.1)
    mutex.release()
    atomValue.value += 1


class CuckooHttpRequest:
    def __init__(self):
        self.proxy = {
            "http": f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}',
            "https": f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}',
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
        elif ua == 'wap':
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
            # "Host": "h5api.m.1688.com",
            "Pragma": "no-cache",
            "Referer": "http://m.1688.com/?src=desktop",
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
        interval_delay()
        print "[INFO]: Seconds: {}, Request_Count: {} ".format(time.time() - self.startTime, atomValue.value)
        return resquests_model.get(url, params=params, **kwargs) if method == "get" else resquests_model.post(url, data=data, json=json, **kwargs)
