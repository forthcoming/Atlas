import re
import sys
sys.path.append('../..')
sys.path.append('../../..')
import json
from atlas.config.settings import *
from jsonpath import jsonpath

reload(sys)
sys.setdefaultencoding('utf-8')


class MatchRes(object):
    def re_match_res(self, res, re_str):
        res = res or ''
        try:
            re_obj = re.findall(re_str, res, re.S)
            res_v = re_obj[0] if re_obj else False
        except:
            res_v = False
        return res_v

    def xpath_match_res(self, res, xpath_str):
        res = res or ''
        pass

    def json_match_res(self, res, jpath_str):
        res = res or ''
        try:
            json_obj = json.loads(res)
            json_v = json_obj.get(jpath_str)
        except:
            json_v = False
        return json_v

