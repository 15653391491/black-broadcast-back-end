# 正则验证格式
DATE_FORMATTER_RE = "[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}"  # 时间
DATE_FORMATTER_RE_PHONE = "[0-9]{8}.[0-9]{6}"  # 设备时间格式
LNGLAT_FORMATTER_RE_PHONE = "[0-9]+.[0-9]+-[0-9]+.[0-9]+"  # 坐标格式
PHONEID_FORMATTER_RE = "[0-9]{15}"
IDCARD_FORMATTER_RE = "[0-9]{18}"
INT_FORMATTER_RE = "[0-9]+"  # 是否为整数
INT_OR_FLOAT = "^[+-]?([0-9]*\.?[0-9]+|[0-9]+\.?[0-9]*)([eE][+-]?[0-9]+)?$"
ADCODE_FORMATTER = "[0-9]{6}"
# 日期格式
DATA_FORMATTER = "%Y-%m-%d %H:%M:%S"  # 日期格式
HEATMAP_DATE_FORMATTER = '%Y/%m/%d'

# 未知设备
UNKNOW_MOBILE = "0" * 15

# 未知人员
UNKNOW_IDCARD = "0" * 18

# 未知区域adcode
UNKNOW_DISTRICT = "0"

# 未知坐标
UNKNOW_LNGLAT = "x,x"

# 未知频点
UNKNOW_WHITELIST = 0

# 未知白名单种类
UNKNOW_WHITECATEGORY = 4

# 未知黑名单种类
UNKNOW_BLACKCATEGORY = 1

# 未知页数
UNKNOW_PAGE = "1"

# 未知每页数据量
UNKNOW_LIMIT = "10"

# 未知时间范围
UNKNOW_TIMERANGE = "-1"

# 未知行政区编码
UNKNOW_ADCODE = "0"

# 频点分类
# WHITE_TYPE = ["普通频点", "干扰频点", "区域频点", "未知种类", "黑广播"]

WHITE_TYPE = [{
    "name": "普通频点",
    "islegal": "1"
}, {
    "name": "区域频点",
    "islegal": "1"
}, {
    "name": "干扰频点",
    "islegal": "1"
}, {
    "name": "未知种类",
    "islegal": "0"
}, {
    "name": "黑广播",
    "islegal": "0"
}]

# 黑广播种类
BC_TYPE = ["未知", "假药", "虚假信息", "政治反动", "恐怖主义", "淫秽色情"]
