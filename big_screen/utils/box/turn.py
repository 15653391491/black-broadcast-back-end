import re
import traceback

from con_control.Serialization import serMobile
from con_brocast.Serialization import serBlackCategory
from big_screen.utils import tools as t
from big_screen.serialization import allSerialization as ser
from big_screen.utils import re_format as f
from big_screen.utils.turn_format import time_formatter, lnglat_formatter


# 黑广播转化
def blackrecord_turn(message):
    """
    移动端发来的数据转化为标准数据(黑广播)
    :param message:
    :return:
    """
    # try:
    mob = serMobile()
    category = serBlackCategory()
    info = message.get("data")
    info_list = list()
    for content in info:
        con = dict()
        con["category"] = category.table.get(num=content["category"])
        con["time"] = t.get_time(content.get("time"))
        con["lnglat"] = t.getLocation(content.pop("location"))
        con["mobile"] = mob.table.get(mobile=content.pop("phoneid"))
        con["record"] = content.get("record") + ".ogg"
        address_info = t.getaddress(con.get("lnglat"))
        con["address"] = address_info["formatted_address"]
        con["adcode"] = address_info["adcode"]
        con["freq"] = content.get("freq")
        con["contact"] = content.get("contact")
        con["common"] = content.get("common")
        info_list.append(con)
    return info_list
    # except Exception:
    # traceback.print_exc()


def blackrecord_turn_text(info_list):
    """
    task测试
    :param info_list:
    :return:
    """
    # *********** 序列化器 ***********
    bro = ser.serBlackRecord()
    # *********** 转化器 **********
    tf = time_formatter()
    lf = lnglat_formatter()
    # ------------ 验证 ---------------
    if len(info_list) is 0:
        info_list = [{
            "category": "",
            "phoneid": "",
            "location": "",
            "freq": "",
            "time": "",
            "record": "",
            "acquisitionmode": "",
            "confidencelevel": ""
        }]
    for info in info_list:
        category = info.get("category")
        time = info.get("time")
        lnglat = info.get("location")
        mobile = info.get("phoneid")
        record = info.get("record") + ".ogg"
        freq = info.get("freq")
        contact = info.get("contact")
        common = info.get("common")
        # *********** 验证 ****************
        category_result = re.fullmatch(f.INT_FORMATTER_RE, category)
        time_result = re.fullmatch(f.DATE_FORMATTER_RE_PHONE, time)
        lnglat_result = re.fullmatch(f.LNGLAT_FORMATTER_RE_PHONE, lnglat)
        mobile = re.fullmatch(f.PHONEID_FORMATTER_RE, mobile)
        freq_result = re.fullmatch(f.INT_OR_FLOAT, freq)
        if type(contact) is not str:
            contact = ""
        if type(common) is not str:
            common = ""
        # ********** 处理 ****************
        if category_result is None:
            category = f.UNKNOW_BLACKCATEGORY
        if time_result is None:
            time = tf.now_time_str
        else:
            time = tf.get_time_str(time)
        if lnglat_result is None:
            lnglat = f.UNKNOW_LNGLAT
        else:
            lnglat = lf.get_lnglat(lnglat)
        if mobile is None:
            mobile = f.UNKNOW_MOBILE
        if freq_result is None:
            freq = f.UNKNOW_WHITELIST
