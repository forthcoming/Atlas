# coding=utf-8
import sys
from match_res import MatchRes
reload(sys)
sys.setdefaultencoding('utf-8')


class AlibabaMatch(MatchRes):
    def match_h5tk(self, res=None):
        re_bool = self.re_match_res(res, ur'ret')
        return re_bool

    def match_list(self, res):
        re_bool = self.re_match_res(res, ur'mtopjsonp20')
        return re_bool

    def match_details(self, res):
        re_bool = self.re_match_res(res, ur'discountPriceRanges|暂时无法查看此商品|该商品无法查看或已下架')
        return re_bool

    def match_seller(self, res):
        re_bool = self.re_match_res(res, ur'archive-baseInfo-companyInfo|该会员暂未发布公司信息！')
        return re_bool

    def match_comment(self, res):
        re_bool = self.re_match_res(res, ur'rates')
        return re_bool
