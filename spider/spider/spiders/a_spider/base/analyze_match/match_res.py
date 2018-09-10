import re
import sys
import json

reload(sys)
sys.setdefaultencoding('utf-8')


class MatchRes(object):
    @staticmethod
    def re_match_res(res, re_str):
        res = res or ''
        try:
            re_obj = re.findall(re_str, res, re.S)
            res_v = re_obj[0] if re_obj else False
        except Exception:
            res_v = False
        return res_v

    @staticmethod
    def xpath_match_res(res, xpath_str):
        res = res or ''
        pass

    @staticmethod
    def json_match_res(res, jpath_str):
        res = res or ''
        try:
            json_obj = json.loads(res)
            json_v = json_obj.get(jpath_str)
        except Exception:
            json_v = False
        return json_v
