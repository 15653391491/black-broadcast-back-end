import os

ISWORKING_RECORD = 2 * 60  # 心跳包记录时间间隔

EXPIRATION_TIME = 2 * 60  # 心跳包过期时间
RECORD_EXPIRATION_TIME = 5 * 60  # 心跳包记录时间过期
BROADCASTING_EXPRIATION_TIME = 1 * 60  # 黑广播记录过期时间
CHART_EXPRIATION_TIME = 24 * 60 * 60  # 图表数据过期时间
MASSMARK_EXPRIATION_TIME = 1 * 60 * 60  # 黑广播实时数据过期时间

STATUSCODE_SUCCESS = 0  # 状态码：成功
STATUSCODE_UNSUCCESS = 1  # 状态码：成功

ISWORKING_SELECTCYCLE = 1 * 60  # 工作手机检索周期
MASSMARK_SELECTCYCLE = 15 * 60  # 黑广播检索周期
CHART_SELECTCYCLE = 30 * 60  # 图表更新周期

DATA_FORMATTER = "%Y-%m-%d %H:%M:%S"  # 日期格式
HEATMAP_DATE_FORMATTER = '%Y/%m/%d'

# 一级行政区代码
UNKNOW = 000000  # 未知
BEIJING = 110000
HEBEI = 130000
FUJIAN = 350000
HENAN = 410000  # 河南
CHONGQING = 500000
GUIZHOU = 520000
NINGXIA = 640000
LIAONING = 210000
JILIN = 220000
SHANXI = 140000
SHANXII = 610000
NEIMENGGU=150000
# 市级行政区
YULINSHI = 610800
# 当前所在以及行政区
SYS_DISTRICT = NEIMENGGU

# 正则验证格式
DATE_FORMATTER_RE = "[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}"  # 时间
DATE_FORMATTER_RE_PHONE = "[0-9]{8}.[0-9]{6}"  # 设备时间格式
LNGLAT_FORMATTER_RE_PHONE = "[0-9]+.[0-9]+-[0-9]+.[0-9]+"  # 坐标格式
PHONEID_FORMATTER_RE = "[0-9]{15}"
IDCARD_FORMATTER_RE = "[0-9]{18}"
INT_FORMATTER_RE = "[0-9]+"

con = {
    "code": STATUSCODE_SUCCESS,
    "msg": "成功"
}

con_false = {
    "code": STATUSCODE_UNSUCCESS,
    "msg": "失败"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
file_DIR = BASE_DIR + "/static/mp3"
if __name__ == '__main__':
    print(file_DIR)
