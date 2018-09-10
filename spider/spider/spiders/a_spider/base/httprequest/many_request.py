# coding=utf-8
import time
from atlas.utils.httprequest import request_model

class ManyRequest:
    def __init__(self):
        self.cuc_req = request_model.CuckooHttpRequest()

    def many_request(self, url,
                     match_func=None,
                     headers=None,
                     **kwargs):
        n = 0
        try_count = 10
        while n < try_count:
            try:
                res = self.cuc_req.get(url, headers=headers, **kwargs)

                if res.status_code == 200:
                    if self.match(match_func, res.text):
                        return res
            except Exception as e:
                print '[INFO]: 数据请求失败...正在重试......', e, url
                n += 1
                time.sleep(5) if n % 3 == 0 else time.sleep(1)

        print "[INFO]: 最终请求失败！！！！！！！！！！！！！！！！！"
        return None

    @staticmethod
    def match(match_func, res):
        if match_func is None:
            return True
        if match_func(res):
            return True
        else:
            raise Exception("[INFO]: 返回值中未匹配到合适的内容！")
