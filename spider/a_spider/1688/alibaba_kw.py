import re
import time
import copy
import json
import Queue
import hashlib
import logging
import datetime
import threading
from lxml import etree
from urllib import quote
from atlas.log.log import Log
from atlas.config.settings import *
from atlas.models.tool.common import on_off_sale
from atlas.utils.request_tools.request_tool import *
from atlas.database.atlasDatabase import AtlasDatabase
from atlas.datamodel.product import Product, HistoryProduct
from atlas.utils.httprequest.many_request import ManyRequest
from atlas.utils.analyze_match.alibaba_match import AlibabaMatch

mutex = threading.Lock()  # 互斥锁，用来协调0.1秒发送请求

class AutoSpider:
    def __init__(self, keyword_queue, atlas_database, **kwargs):
        # time 2018-8-28-13-57#
        # add keyword parameter: **kwargs
        # add object property: self.category_queue = kwargs.get('category_q')#
        self.category_kw_queue = kwargs.get('category_kw_q')
        # ------------------ending-------------------------#
        self.product = Product()
        self.manyreq = ManyRequest()
        self.amatch = AlibabaMatch()

        self.kwQueue = keyword_queue
        self.Database = atlas_database

        self.db_client = MONGO_URI
        self.db_database = MONGO_ATLAS

        self.params = aliparams
        self.headers = copy.copy(aliheaders)
        print self.headers
        try:
            self.sum = int(PRODUCT_SUM)
        except Exception:
            self.sum = float('inf')

    def extract_queue(self):
        info = self.kwQueue.get(block=False)
        kw_name = info[1].replace('"', '').replace("'", '')
        kw_name = kw_name.replace('\n', '').replace('\r', '')
        kw_name = kw_name.replace('\t', '').replace('\\', '').encode('utf-8')
        category = info[0]
        set_name = "product_%s" % category
        history_set_name = "history_1688_%s" % category
        print '*' * 100, self.sum
        return kw_name, category, set_name, history_set_name

    def __h5tk(self):
        url = alih5url
        res = self.manyreq.many_request(url,
                                        match_func=self.amatch.match_h5tk,
                                        headers=self.headers,
                                        **self.params)
        cookies = res.cookies.get_dict()
        h5_tk = cookies['_m_h5_tk'].split('_')[0]
        print '[INFO]: h5_tk: ', h5_tk
        string = '; '.join(key + "=" + value for key, value in cookies.items()) + '; '
        self.headers['Cookie'] = string + alicookie
        return h5_tk

    @staticmethod
    def __signlink(kw_name, h5_tk, begin_page):
        millis = int(time.time() * 1000)
        data = '{{"sortType":"pop","keywords":"{}","filtId":"","appName":"wap","beginPage":{},"pageSize":60}}'.format(
            kw_name, begin_page)
        print "[INFO]: data：{}".format(data)
        string = h5_tk + '&' + str(millis) + "&12574478&" + data
        data = quote(data)
        m2 = hashlib.md5()
        m2.update(string)
        sign = m2.hexdigest()
        link = 'http://h5api.m.1688.com/h5/mtop.1688.offerservice.getoffers/1.0/?jsv=2.4.11&appKey=12574478&t=' + str(
            millis) + '&sign=' + sign + '&api=mtop.1688.offerService.getOffers&v=1.0&type=jsonp&dataType=jsonp&' \
                                        'callback=mtopjsonp20&data=%s' % data
        print '\n'
        return link

    def __analyze_list_info(self, link):
        try:
            p_res = self.manyreq.many_request(link,
                                              match_func=self.amatch.match_list,
                                              headers=self.headers,
                                              **self.params).text
        except Exception:
            return False
        res = re.findall(r'mtopjsonp20\((.*)\)', p_res, re.S)[0]
        json_obj = json.loads(res)
        flag = json_obj.get("data", {}).get("offers", [])
        if flag:
            id_list = json_obj.get("data", {}).get("offers", [])
            p_id_li = [pid.get("id", "") for pid in id_list]
            return p_id_li
        else:
            return False

    def __get_pid(self, kw_name, h5_tk):
        begin_page = 1
        no_value = False
        p_id_big_li = []
        while True:
            link = self.__signlink(kw_name, h5_tk, begin_page)
            p_id_li = self.__analyze_list_info(link)
            if not p_id_li:
                if no_value:
                    print '[INFO]: 已无更多商品！！！'
                    break
                else:
                    print "[INFO]: warnning!!! 没找到与“%s”相关的商品" % kw_name
                    # TODO 此处可以写入日志
                    break
            p_id_big_li.extend(p_id_li)
            length = len(p_id_big_li)
            print "[INFO]: 当前商品数量：{}".format(length)
            if length > 0:
                no_value = True

            if length >= self.sum:
                print '-' * 100
                break
            else:
                begin_page += 1
        return p_id_big_li

    @staticmethod
    def __integer(prices):
        # price = int(float(prices.split("-")[0]) * 100) if prices else 0  # 最小价格
        price = int(float(prices.split("-")[-1]) * 100) if prices else 0  # 最大价格
        return price

    @staticmethod
    def __float(num):
        price = int(float(num.split("-")[0])) if num else 0
        return price

    @staticmethod
    def __int(num):
        price = int(float(num.split("-")[0])) if num else 0
        return price

    def __product_detail(self, p_id_big_li, category, kw_name):
        p_id_big_li = p_id_big_li[:self.sum] if isinstance(self.sum, int) else p_id_big_li
        # p_id_big_li = ["556781441758", "567106814327", "568511074645", "520589497412"]
        length = len(p_id_big_li)
        for n in range(length):
            pid = p_id_big_li[n]
            product_dict = Product()
            history_dict = HistoryProduct()
            system_id = "1688_%s" % pid.encode('utf-8')
            print "[INFO]: 正在请求 >>> “%s”关键字的第%s件商品。。。。。。" % (kw_name, str(n+1))
            print "[INFO]: system_id : ", system_id
            node = self.Database.db['cluster_node_{}'.format(category)]

            url = "https://m.1688.com/offer/%s.html" % pid
            print "[INFO]: thread_name", threading.current_thread().getName(), 'start'
            res = self.manyreq.many_request(url,
                                            match_func=self.amatch.match_details,
                                            headers=self.headers,
                                            **self.params)
            print "[INFO]: thread_name", threading.current_thread().getName(), 'end'
            if ("暂时无法查看此商品" in res.text) or ("该商品无法查看或已下架" in res.text) or not res:
                on_off_sale(node, system_id, False)
                print "[INFO]: %s 商品已下架！！！！！" % system_id
                continue
            try:
                html = etree.HTML(res.text)
                p_info_json = html.xpath('//*[@id="wing-page-content"]/div/script[2]//text()')[0] + '&end&'
                p_detail_info = re.findall(r'window.wingxViewData\[0\]=(.*)&end&', p_info_json)[0]
                # print "[INFO]: p_detail_info", p_detail_info
                p_info_json = json.loads(p_detail_info)
                is_off_sale = p_info_json.get('isOffSale', '')
                if is_off_sale == 'true':
                    on_off_sale(node, system_id, False)
                    print "[INFO]: %s 商品已下架！！！！！\n" % system_id
                    continue
                detail_dict = self.__analyze_detail(pid, p_info_json)

                product_dict.system_id = system_id
                product_dict.product_id = pid
                product_dict.currency = "¥"
                product_dict.image = detail_dict.get("image_list")
                product_dict.keywords = kw_name
                product_dict.platform = "1688"
                product_dict.price = detail_dict.get("lt_price")
                product_dict.product_url = "https://detail.1688.com/offer/%s.html" % pid
                product_dict.sales = detail_dict.get("saled_count")
                product_dict.title = detail_dict.get("p_name")
                product_dict.is_hash = False
                product_dict.ext_price = detail_dict.get("ext_price")

                history_dict.keywords = kw_name
                history_dict.category = category
                history_dict.system_id = system_id
                history_dict.price = detail_dict.get("lt_price")
                history_dict.inventory = detail_dict.get("canbook_count")
                history_dict.record_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                ext_dict = dict()
                ext_dict["user_id"] = detail_dict.get("user_id")
                ext_dict["offer_id"] = detail_dict.get("offer_id")
                ext_dict["member_id"] = detail_dict.get("member_id")

                # 最好是插入成功后传入
                on_off_sale(node, system_id, True)

                yield product_dict, history_dict, ext_dict

            except Exception:
                pass

    def __analyze_detail(self, pid, p_info_json):
        ext_price_list = []
        user_id = p_info_json.get("userId", '')
        p_name = p_info_json.get("subject", '')
        offer_id = p_info_json.get("offerId", '')
        member_id = p_info_json.get("memberId", '')
        saled_count = p_info_json.get("saledCount", '')
        is_sku_offer = p_info_json.get("isSKUOffer", '')
        comment_totals = p_info_json.get("rateTotals", '')
        star_level = p_info_json.get("rateAverageStarLevel", '')
        is_sku_offer = True if is_sku_offer == "true" else False
        image_list = [img_kw.get("originalImageURI", '') for img_kw in p_info_json.get("imageList", [])]

        ext_price = p_info_json.get('priceRanges', [])
        # 折扣价格
        lt_price = p_info_json.get("skuDiscountPrice", '0')
        # 默认价格
        lt_price = lt_price if lt_price else p_info_json.get("priceDisplay", '0')
        for price_dict in ext_price:
            price_list = []
            for k, v in price_dict.items():
                if k in ["price", "convertPrice"]:
                    price_list.append([k, self.__integer(v)])
                else:
                    price_list.append([k, self.__int(v)])
            ext_price_list.append(price_list)
        # for i in ext_price_list:
        #     print i

        if is_sku_offer:
            sku_map = p_info_json.get("skuMap", {})
            # 库存（分类库存）
            canbook_count = [[key, self.__int(value.get("canBookCount", 0))] for key, value in sku_map.items()]
            # 以下3行是另外一种其他价格，内容是商品属性分类价格
            # mrak = re.findall('"discountPrice"', json.dumps(sku_map))
            # if mrak:
            #     ext_price = [[key, self.__integer(value["discountPrice"])] for key, value in sku_map.items()]

        else:
            # 库存（总库存）
            canbook_count = [["库存", self.__int(p_info_json.get("canBookedAmount", 0))]]

        ext_price = ext_price_list if ext_price_list else [["other_price", self.__integer(lt_price)]]
        lt_price = self.__integer(lt_price)
        saled_count = self.__int(saled_count)
        comment_totals = self.__int(comment_totals)

        detail_dict = {
             "p_name": p_name,
             "image_list": image_list,
             "lt_price": lt_price,
             "saled_count": saled_count,
             "ext_price": ext_price,
             "canbook_count": canbook_count,
             "user_id": user_id,
             "offer_id": offer_id,
             "member_id": member_id,
            }

        return detail_dict

    def __seller_info(self, member_id, product_dict, history_dict):
        seller_info_li = []
        contact_information = {}
        url = "https://m.1688.com/winport/company/%s.html" % member_id
        res = self.manyreq.many_request(url,
                                        match_func=self.amatch.match_seller,
                                        headers=self.headers,
                                        **self.params).text or ''

        html = etree.HTML(res)
        if re.findall(r'该会员暂未发布公司信息！', res, re.S) or html is None:
            company_name = contact_address = phone_num = ''
        else:
            try:
                xpath_str1 = '//*[@id="scroller"]/div[@class="archive-baseInfo-companyInfo"]/ul/li[1]/div/span/text()'
                xpath_str2 = '//*[@id="scroller"]/div[@class="archive-baseInfo-contactInfo"]/ul/li[2]/div/span/text()'
                company_name = html.xpath(xpath_str1)
                contact_address = html.xpath(xpath_str2)
                phone_num = re.findall(r'archive-sheet-item phone">(.*?)</div>', res, re.S)
            except Exception:
                company_name = contact_address = phone_num = ''
        contact_information["phone_num"] = '/'.join(phone_num)
        contact_information["contact_address"] = ''.join(contact_address)
        seller_info_li.extend([''.join(company_name), contact_information])
        product_dict.seller_name = history_dict.seller_name = ''.join(company_name)
        product_dict.contact = contact_information

    def __comment_info(self, offer_id, user_id, product_dict):
        page = 1
        star_level = ''
        comment_info_li = []
        millis = int(time.time() * 1000)
        url = "https://rate.1688.com/remark/offerDetail/rates.json?"
        params = {
            "_input_charset": "GBK",
            "offerId": offer_id,
            "page": page,
            "pageSize": "15",
            "starLevel": star_level,
            "orderBy": "date",
            "semanticId": "",
            "showStat": "0",
            "content": "1",
            "t": millis,
            "memberId": user_id,
        }
        url += ''.join(key + '=' + str(value) + '&' for key, value in params.items())
        res = self.manyreq.many_request(url,
                                        match_func=self.amatch.match_comment,
                                        headers=self.headers,
                                        **self.params).text or ''
        if res:
            try:
                json_obj = json.loads(res)
                comment_flag = json_obj.get("data", {}).get("rates", [])
                member_name = [cmt_dict.get("member", '') for cmt_dict in comment_flag]
                comment_date = [rateitem for cmt_dict in comment_flag for rateitem in cmt_dict.get("rateItem", [])]
                n = 0
                for i in comment_date:
                    i.pop('starLevel', '404')
                    i.pop('explainTime', '404')
                    i.pop('explainContent', '404')
                    i['member'] = member_name[n]
                    comment_info_li.append(i)
                    n += 1
            except Exception:
                pass

        print "[INFO]: 评论内容：", comment_info_li
        product_dict.comment = comment_info_li

    def storage(self, product_dict, history_dict):
        system_id = product_dict.system_id.encode('utf-8')
        old_record = self.Database.findOneProduct(history_dict.category, {"system_id": system_id})
        if not old_record:
            self.Database.insertOrUpdateProduct(history_dict.category, product_dict)
        else:
            self.Database.insertOrUpdateProduct(history_dict.category, product_dict,
                                                exclude_keys=["is_hash", "comment"])

        self.Database.insertHistory(history_dict.category, history_dict, product_dict.platform)

    # mian函数，处理所有关键字，get一个关键字进行爬取
    @Log(level=logging.INFO, name='Alibaba.log')
    def main(self, *args):
        # time 2018-8-30-9-54 #
        # 记录最新更新的时间
        dt = (datetime.datetime.now()).strftime('%Y-%m-%d')
        # ------------------ending-------------------------#

        while not self.kwQueue.empty():
            kw_name, category, set_name, history_set_name = self.extract_queue()
            try:
                h5_tk = self.__h5tk()
            except Exception:
                # TODO 这里不建议使用 continue 出现错误时会跳过当前关键字！！！！
                continue
            p_id_big_li = self.__get_pid(kw_name, h5_tk)
            for product_dict, history_dict, ext_dict in self.__product_detail(p_id_big_li, category, kw_name):
                self.__seller_info(ext_dict.get("member_id"), product_dict, history_dict)
                # self.__comment_info(ext_dict.get("offer_id"), ext_dict.get("user_id"), product_dict)
                self.storage(product_dict, history_dict)

        # time 2018-8-28-13-57 #
        print '++++++++++update program starting++++++++++'
        time.sleep(5)
        while not self.category_kw_queue.empty():
            category, kw_name = self.category_kw_queue.get(block=False)
            product_id_list, category_name, kw_name = query_data(self.Database, category, kw_name, dt)
            for product_dict, history_dict, ext_dict in self.__product_detail(product_id_list, category_name, kw_name):
                self.__seller_info(ext_dict.get("member_id"), product_dict, history_dict)
                # self.__comment_info(ext_dict.get("offer_id"), ext_dict.get("user_id"), product_dict)
                self.storage(product_dict, history_dict)
        # ------------------ending-------------------------#


if __name__ == '__main__':
    MONGO_URI = "mongodb://192.168.105.20:27017"
    MONGO_ATLAS = "atlas_test1"
    keywordQueue = Queue.Queue()
    Database = AtlasDatabase(MONGO_URI, MONGO_ATLAS)
    keywordQueue.put(("women", "连衣裙"))
    As = AutoSpider(keywordQueue, Database, category_kw_q=keywordQueue)
    As.main()
