from atlas.utils.mapping.JsonModelMapping import JsonModelMapping

class SubCategory(JsonModelMapping):
    platform = ''           # 平台名
    keyword = []            # 关键字
    source = ''             # 数据源


class CategoryInfo(JsonModelMapping):
    name = ''           # 中文名
    name_en = ''        # 英文名，用于标识分类
    sub_category = []   # dict组成的key->value对，platform keyword
    max_diff = 0        # phash 计算的diff
    machine_id = ''     # 分配到哪台设备