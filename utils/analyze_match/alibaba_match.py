# coding=utf-8
import sys
from match_res import MatchRes
reload(sys)
sys.setdefaultencoding('utf-8')


class AlibabaMatch(MatchRes):
    def match_h5tk(self, res=None):
        re_bool = self.re_match_res(res, r'ret')
        return re_bool

    def match_list(self, res):
        re_bool = self.re_match_res(res, r'mtopjsonp20')
        return re_bool

    def match_details(self, res):
        re_bool = self.re_match_res(res, r'discountPriceRanges')
        return re_bool

    def match_seller(self, res):
        re_bool = self.re_match_res(str(res), r'archive-baseInfo-companyInfo|该会员暂未发布公司信息！')
        return re_bool

    def match_comment(self, res):
        re_bool = self.re_match_res(res, r'rates')
        return re_bool
