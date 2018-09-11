import re
import time
import json
import random
import jsonpath
import requests
from lxml import etree

class Taobao_Comment:

    def header(self):
        headers = {
            'authority': 'detail.tmall.com',
            'method': 'GET',
            'scheme': "https",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'cache-control': "max-age=0",
            'cookie': "cna=XTyQEoI1uE4CAXBfh3IMFSpJ; cq=ccp%3D1; t=4d814acaeff7745d2b1df5c531cb7227; _tb_token_=3eb56ee77e988; cookie2=17B3F5F8A0D9CB4142FFBB0733EC948B; pnm_cku822=098%23E1hvApvUvbpvjQCkvvvvvjiPPL5wljtVP25hgjivPmPy1jYRRsdvzjiRR2z91jQPvpvhvvvvvvhCvvOvUvvvphvEvpCWh8%2Flvvw0zj7OD40OwoAQD7zheutYvtxr1RoKHkx%2F1RBlYb8rwZBleExreE9aWXxr1noK5FtffwLyaB4AVAdyaNoxdX3z8ikxfwoOddyCvm9vvvvvphvvvvvv96Cvpv9hvvm2phCvhRvvvUnvphvppvvv96CvpCCvkphvC99vvOC0B4yCvv9vvUvQud1yMsyCvvpvvvvviQhvCvvv9UU%3D; isg=ArOzZnnX7QJos6HBeuocdKfGQrcdQCLrPU38GWVQTFIJZNMG7bjX-hH2aqJx",
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
            "referer": "https://item.taobao.com/item.htm?spm=a219r.lmn002.14.174.6f516358W81jq9&id=561495525977&ns=1&abbucket=16",
        }
        return headers

    def comment(self, request, match, pid, **params):
        self.resp_code = ""
        # 不携带currentPageNum参数看不到数据,不携带rateType参数数据顺序会乱(3为带图片评论)
        url = 'https://rate.taobao.com/feedRateList.htm?auctionNumId=%s&currentPageNum=1&rateType=' % pid
        # headers = {
        #
        #     "cookie": "ubn=p; ucn=unsz; t=28edc35882e1fcf06bfaa67008da2a8f; cna=XTyQEoI1uE4CAXBfh3IMFSpJ; thw=cn; miid=6347655561018672771; uc3=sg2=WqIrBf2WEDhnXgIg9lOgUXQnkoTeDo019W%2BL27EjCfQ%3D&nk2=rUs9FkCy6Zs6Ew%3D%3D&id2=VWeZAHoeqUWF&vt3=F8dBzLgoJIN4WC0X30I%3D&lg2=VFC%2FuZ9ayeYq2g%3D%3D; lgc=%5Cu6211%5Cu6210%5Cu4F60%5Cu5669%5Cu68A6; tracknick=%5Cu6211%5Cu6210%5Cu4F60%5Cu5669%5Cu68A6; _cc_=WqG3DMC9EA%3D%3D; tg=0; enc=GtOY%2B8mhUi7LXIrV9LqmUl0PYsVpr9BbSzEB9GL%2Fq3i6Czwxxh5mE60CMJjep9GIq4iV04PvQsAGhzOIdrf6iw%3D%3D; mt=ci=-1_0; UM_distinctid=160fe373fd7c89-0f04cad75d123e-393d5f0e-1fa400-160fe373fd8e5a; hng=CN%7Czh-CN%7CCNY%7C156; _m_h5_tk=081b6ec244bfd7ba155325c85a14056e_1516103738466; _m_h5_tk_enc=8531a9b39cfb4a076e45dfad1fba7525; cookie2=16e0f40738dc82c43c53992cb5a26ebb; _tb_token_=3daeebbb3768e; v=0; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; uc1=cookie14=UoTdfYT5TUo4kA%3D%3D; isg=BDo6USLQNOpL5rgFeJZzPiuWi2CcQ9uEDF5FrkQyJ02YN9lxLHiA1B8ng8PrpzZd",
        #     "referer": "https://item.taobao.com/item.htm?spm=a219r.lmn002.14.174.6f516358W81jq9&id=561495525977&ns=1&abbucket=16",
        #     "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        #     # "user-agent": user_agent,
        # }
        html = request(url,
                       headers=self.header(),
                       match_func=match,
                       **params).text
        html = html.strip()
        html = html.strip("()")
        res = json.loads(html)
        cmt_res_li = res.get("comments", [])
        # 所有评论日期
        str_date = [cmt_dict.get("date", '') for cmt_dict in cmt_res_li]
        # str_date = jsonpath.jsonpath(res, expr='$..comments[*].date')
        # 获取所有评论人
        str_name = [cmt_dict.get("user", {}).get("nick", '') for cmt_dict in cmt_res_li]
        # str_name = jsonpath.jsonpath(res, expr='$..comments[*].user.nick')
        # 获取所有文字评论,除追加评论外
        str_info = [cmt_dict.get("content", '') for cmt_dict in cmt_res_li]
        # str_info = jsonpath.jsonpath(res, expr='$..comments[*].content')

        comment_info_list = []
        # 商品没有评价就退出
        if not str_name:
            print '此商品没有任何评价内容!!!!!'
            return comment_info_list

        comment_data = [x for x in zip(str_name, str_date, str_info)]
        for p, d, i in comment_data:  # p:评论人 d:评论时间 i:评论内容
            comment_info_dict = {}
            comment_info_dict["buyer_id"] = p
            comment_info_dict["cmt_date"] = d
            comment_info_dict["cmt_content"] = i
            comment_info_list.append(comment_info_dict)
            # print p,'---', d, ':',  i
        return comment_info_list

if __name__ == '__main__':
    tc = Taobao_Comment()
    id = '560301942354'  # 521435492569 560301942354
    # category_name = 'LHZ_0222'
    # dir_name = '生活用品_家居用品'
    tc.comment(id)
    print "[INFO]: %s商品所有评论内容已抓取完成！！\n" % (id)

