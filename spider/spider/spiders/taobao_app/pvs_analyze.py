import time
import json

def __integer(prices):
    price = int(prices) * 100 if prices else 0
    return price


def __int(num):
    price = int(num) if num else 0
    return price


def product_details(stack_data):
    print "[INFO]: stack_data：", json.dumps(stack_data)
    splice_dict = json.loads(stack_data.get("splice", {}))
    has_skuBase = True
    pvs_dict = {}
    props_li = []
    ext_price = []
    image_list = []
    stock_list = []
    lt_price_li = []
    buy_enable = splice_dict.get("trade", {}).get("buyEnable", '')
    # TODO 下架逻辑不严谨  id = 564650758899 可能是暂时无法购买
    if buy_enable == "false":
        return 'off_sales'

    p_name = stack_data.get("data", {}).get("item", {}).get("title", '')
    seller_name = stack_data.get("data", {}).get("seller", {}).get("shopName", '')
    if not seller_name:
        return 'off_sales'

    pri_sto_li = splice_dict.get("skuCore", {}).get("sku2info", {})
    comment_count = stack_data.get("data", {}).get("item", {}).get("commentCount", '')

    sell_count = splice_dict.get("item", {}).get("sellCount", '')
    sell_count = __int(sell_count[0]) if sell_count else None

    # -------------------------------------
    props_value = splice_dict.get("skuBase", {}).get("props", [])
    color_image_list = [values_dict.get("image", '') for props_dict in props_value for values_dict in props_dict.get("values", [])]
    color_image_list_two = stack_data.get("data", {}).get("item", {}).get("image", [])
    color_image_list = color_image_list if color_image_list else color_image_list_two
    turn_image_list = stack_data.get("data", {}).get("item", {}).get("images", [])
        
    image_list.extend(turn_image_list)
    image_list.extend(color_image_list)
    image_list = map(lambda x: "https:" + x, image_list)

    contact_address = splice_dict.get("delivery", {}).get("from", None)
    props_li = stack_data.get("data", {}).get("skuBase", {}).get("props", [])
    if props_value:
        props_li = props_value
    elif props_li:
        props_li = props_li
    else:
        lt_price = __integer(float(pri_sto_li.get('0', {}).get("price", {}).get("priceText", '0')))
        stock_num = __int(pri_sto_li.get('0', {}).get("quantity", '0'))
        lt_price_li.append(lt_price)
        ext_price.append(['价格', lt_price])
        stock_list.append(['库存', stock_num])
        has_skuBase = False

    if has_skuBase:
        pvs_str_li = splice_dict.get("skuBase", {}).get("skus", [])
        pvs_str_li = pvs_str_li if pvs_str_li else stack_data.get("data", {}).get("skuBase", {}).get("skus", [])
        for props in props_li:
            pvs_dict[props["pid"]] = props["name"]
            values = props["values"]
            for value in values:
                pvs_dict[value["vid"]] = value["name"]

        for sku_d in pvs_str_li:
            pv_s_li = []
            pvs = sku_d['propPath']
            sku = sku_d['skuId'].encode('utf-8')
            pvs_li = pvs.split(';')
            for pv_s in pvs_li:
                pv_s_li.extend(pv_s.split(':'))

            s = ''
            for key in pv_s_li[1::2]:
                s += pvs_dict[key] + '|'

            stock = price = 0
            if pri_sto_li.get(sku, False):
                price = __integer(float(pri_sto_li[sku]['price']['priceText']))
                stock = __int(pri_sto_li[sku]['quantity'])
                lt_price_li.append(price)

            stock_list.append([s, stock])
            ext_price.append([s, price])

    lt_price = sorted(lt_price_li)[0]  # 最小价格
    # lt_price = sorted(lt_price_li)[-1]  # 最大价格

    p_info_dict = {
        'p_name': p_name,
        'lt_price': lt_price,
        'ext_price': ext_price,
        'image_list': image_list,
        'sell_count': sell_count,
        'stock_dict': stock_list,
        'seller_name': seller_name,
        'comment_count': comment_count,
        'contact_address': contact_address,
    }
    return p_info_dict
