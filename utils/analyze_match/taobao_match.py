import json
from match_res import MatchRes


class TaobaoMatch(MatchRes):
    def match_list(self, res=None):
        re_bool = self.re_match_res(res, r'totalPage')
        return re_bool

    def match_h5tk(self, res=None):
        re_bool = self.re_match_res(res, r'ret')
        return re_bool

    def match_details(self, res=None):
        js_bool = False
        try:
            re_bool = self.re_match_res(res, r'mtopjsonp2\((.*)\)')
            json_obj = json.loads(re_bool)
            apistack = json_obj.get("data", {}).get("apiStack", [])
            for api_dict in apistack:
                js_bool = api_dict.get("value", '')
        except: pass
        return js_bool

    def match_comments(self, res=None):
        re_bool = self.re_match_res(res, r'comments')
        return re_bool
