# coding=utf-8
import re
import sys
import time
import json
import jsonpath
sys.path.append('../../..')
from atlas.utils.httprequest import request_model
# from cuckoo_atlas.atlas.utils.httprequest import request_model
reload(sys)
sys.setdefaultencoding('utf-8')


class ManyRequest(object):
    def __init__(self):
        self.cuc_req = request_model.CuckooHttpRequest()
        self.headers = {}

    def many_request(self, url, headers=None, **kwargs):
        resp = False
        flag = False
        params = {'proxies': True, 'session': True, 'headers': headers, 'ua': 'mob', 'timeout': 15}

        try:
            mark = mark_b = mark_c = mark_d = True
            print '[INFO]: 正在请求：', url
            if kwargs:
                print '[INFO]: 过滤模式：', kwargs
                if kwargs['match'] == 1:
                    res = self.cuc_req.get(url, **params)
                    mark = re.findall(r'ret', res.text, re.S)
                elif kwargs['match'] == 2:
                    res = self.cuc_req.get(url, **params)
                    res_j = re.search(r'mtopjsonp2\((.*)\)', res.text, re.S)
                    res_j = res_j.group(1) if res_j else False
                    mark_b = jsonpath.jsonpath(json.loads(res_j),
                                               expr='$.data.apiStack[*].value') if res_j else False
                    mark_b = mark_b[0] if res_j and mark_b else False
                elif kwargs['match'] == 3:
                    res = self.cuc_req.get(url, **params)
                    mark_c = re.findall(r'rates', res.text, re.S)
                elif kwargs['match'] == 4:
                    res = self.cuc_req.get(url, **params)
                    mark_d = re.findall(r'totalPage', res.text, re.S)
                else:
                    res = self.cuc_req.get(url, **params)

            else:
                res = self.cuc_req.get(url, **params)
            if res.status_code == 200 and mark and mark_b and mark_c and mark_d:
                resp = res
            else:
                raise Exception(res.status_code)

        except Exception as e:
            print '[INFO]: 数据请求失败...正在重试......', e, url
            with open('request.log', 'a') as f:
                s = sys.exc_info()
                err = "Error {} happened on line {}".format(s[1], s[2].tb_lineno)
                print '[INFO]: %s' % err
                f.write('{} >> 请求失败({}) - {}\n'.format(url, err, time.ctime()))
            # # global NETWORK_STATUS
            NETWORK_STATUS = False  # 请求超时改变状态

            if not NETWORK_STATUS:
                #     '请求超时'
                for i in range(1, 11):
                    time.sleep(1)
                    print '[INFO]: 请求失败，第%s次重复请求' % i
                    if i == 5:
                        print "[INFO]: 程序睡眠中......"
                        time.sleep(30)
                    if i == 7:
                        print "[INFO]: 程序睡眠中......"
                        time.sleep(60)
                    if i == 9:
                        print "[INFO]: 程序睡眠中......"
                        time.sleep(360)

                    try:
                        mark = mark_b = mark_c = mark_d = True
                        print '[INFO]: 正在请求：', url
                        if kwargs:
                            print '[INFO]: 过滤模式：', kwargs
                            if kwargs['match'] == 1:
                                res = self.cuc_req.get(url, **params)
                                mark = re.findall(r'ret', res.text, re.S)
                            elif kwargs['match'] == 2:
                                res = self.cuc_req.get(url, **params)
                                res_j = re.search(r'mtopjsonp2\((.*)\)', res.text, re.S)
                                res_j = res_j.group(1) if res_j else False
                                mark_b = jsonpath.jsonpath(json.loads(res_j),
                                                           expr='$.data.apiStack[*].value') if res_j else False
                                mark_b = mark_b[0] if res_j and mark_b else False
                            elif kwargs['match'] == 3:
                                res = self.cuc_req.get(url, **params)
                                mark_c = re.findall(r'rates', res.text, re.S)
                            elif kwargs['match'] == 4:
                                res = self.cuc_req.get(url, **params)
                                mark_d = re.findall(r'totalPage', res.text, re.S)
                            else:
                                res = self.cuc_req.get(url, **params)

                        else:
                            res = self.cuc_req.get(url, **params)

                        if res.status_code == 200 and mark and mark_b and mark_c and mark_d:
                            resp = res
                            with open('request.log', 'a') as f:
                                f.write('%s 重新请求成功 - %s\n' % (url, time.ctime()))
                            print '[INFO]:重发请求成功!!!!!!!!!!'
                            flag = True
                            break
                        else:
                            raise Exception(res.status_code)
                    except:
                        with open('request.log', 'a') as f:
                            s = sys.exc_info()
                            err = "Error {} happened on line {}".format(s[1], s[2].tb_lineno)
                            print '[INFO]: %s' % err
                            f.write('{} >> 重新请求失败({}) 继续重试... - {}\n'.format(url, err, time.ctime()))
                        print '[INFO]:重发请求失败!!!!!!!!!!'
                        print '[INFO]: 第%s次重复请求失败! 继续重试...' % i
                        continue

                if flag:
                    with open('request.log', 'a') as f:
                        f.write('%s 最终请求成功!!!!! - %s\n' % (url, time.ctime()))
                    print '[INFO]:最终请求成功!!!!!!!!!!'
                else:
                    with open('request.log', 'a') as f:
                        f.write('最终请求失败%s ! ! ! ! ! - %s\n' % (url, time.ctime()))
                    print '[INFO]:最终请求失败%s!!!!!!!!!!'
        if resp == '':
            print 'ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'

        return resp