import datetime
import logging

from .models import BlackRecord, BlackCategory
from big_screen.utils import sys_setting as code, tools as t
from big_screen.utils.box import Serialization as ser

errlog = logging.getLogger("Process")


class serBlackCategory(ser.SerTable):
    def __init__(self):
        ser.SerTable.__init__(self)
        self.table = BlackCategory.objects


class serBlackRecord(ser.SerTable):
    def __init__(self):
        ser.SerTable.__init__(self)
        self.table = BlackRecord.objects
        self.wh = t.GetWhiteList()
        self.wh_region = t.GetWhiteList("1")

    def get_info(self):
        """
        经过白名单过滤,格式转化
        :return:
        """
        _query = self.table.all().values("id", "time", "freq", "lnglat", "category__name", "mobile__name", "record",
                                         "address",
                                         "contact", "common").order_by("-time").exclude(islegal=1)
        # ------------------------- 白名单过滤 -----------------------------
        for k, v in self.wh_region.items():
            _query = _query.exclude(district=k, freq__in=v)
        # ------------------------ 格式化结果 ------------------------------
        contant = self.formatter_content(list(_query))
        return contant

    def select_info(self, select_dict):
        # ------------------------------------------------ 验证 ---------------------------------------------------
        if type(select_dict) is not dict:
            return {"code": code.STATUSCODE_UNSUCCESS, "msg": "参数必须为一个字典"}
        # ------------------------------------------------ 查询集 -------------------------------------------------
        _query = self.table.values("id", "time", "freq", "lnglat", "category__name", "mobile__name", "record",
                                   "address",
                                   "contact", "common").order_by("-time").exclude(islegal=1)
        # ------------------------------------------------ 查询条件 -----------------------------------------------
        keys = select_dict.keys()
        if "s_time" in keys and "e_time" in keys:
            if type(select_dict["s_time"]) is str:
                s_time = datetime.datetime.strptime(select_dict["s_time"], code.DATA_FORMATTER)
                e_time = datetime.datetime.strptime(select_dict["e_time"], code.DATA_FORMATTER)
            else:
                s_time = select_dict["s_time"]
                e_time = select_dict["e_time"]
            _query = _query.filter(time__gte=s_time, time__lte=e_time)
        if "category" in keys:
            category = select_dict["category"]
            if category is not "0":
                _query = _query.filter(category__num=category)
        if "mobile" in keys:
            mobile = select_dict["mobile"]
            if mobile is not "0":
                _query = _query.filter(mobile__mobile=mobile)
        if "freq" in keys:
            freq = select_dict["freq"]
            if freq is not "0" and freq is not "":
                freq = t.freq_interface_to_sql(freq)
                _query = _query.filter(freq=freq)
        if "district" in keys:
            district = select_dict["district"]
            _query = _query.filter(district=district)
        # ------------------ 白名单过滤 -----------------
        for k, v in self.wh_region.items():
            _query = _query.exclude(district=k, freq__in=v)
        contant = self.formatter_content(list(_query))
        return contant

    def count_by_category(self, select_dict):
        """
        根据时间进行种类统计
        :param select_dict:
        :return:
        """
        s_time = datetime.datetime.strptime(select_dict.get("start"), code.DATA_FORMATTER)
        e_time = datetime.datetime.strptime(select_dict.get("end"), code.DATA_FORMATTER)
        # ------------------------- 查询集 -------------------------------------------
        bro_info = self.table.filter(time__gte=s_time, time__lte=e_time)
        # -------------------------
        s = serBlackCategory()
        category_list = s.get_info()
        # ------------------------- 组织数据 --------------------------
        info = list()
        for category in category_list:
            info.append({
                "name": category.get("name"),
                "value": bro_info.filter(category_id=category.get("id")).count()
            })
        return info

    def get_info_obj(self):
        """
        经过白名单过滤,获取查询集
        :return:
        """
        _query = self.table.all().values("id", "time", "freq", "lnglat", "category__name", "mobile__name", "record",
                                         "address",
                                         "contact", "common").order_by("-time").exclude(islegal=1)
        # for k, v in self.wh_region.items():
        #     _query = _query.exclude(district=k, freq__in=v)
        return _query
