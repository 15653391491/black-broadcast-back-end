from django_redis import get_redis_connection
import json

from .BaseOpration import BaseOpration
from big_screen.utils import tools as t
from big_screen.serialization.allSerialization import serMobile
from big_screen.utils import re_format as f


class defaultOp(BaseOpration):
    def __init__(self):
        BaseOpration.__init__(self)
        self.con = get_redis_connection("default")


class sessionOp(BaseOpration):
    def __init__(self):
        BaseOpration.__init__(self)
        self.con = get_redis_connection("session")


class isworkingOp(BaseOpration):
    def __init__(self):
        BaseOpration.__init__(self)
        self.con = get_redis_connection("isworking")
        self.mob = serMobile()

    def formatter_info(self, info):
        """
        格式转换
        :param info:
        :return:
        """
        lnglat = info.get("lnglat")
        address = t.getaddress(lnglat)
        if address is 0:
            address = {
                "status": 1,
                "district": f.UNKNOW_DISTRICT,
                'formatted_address': "",
                "data_from": "",
                "adcode": f.UNKNOW_DISTRICT
            }
        info["address"] = address
        return (info.get("mobile"), info)


class massmarkOp(BaseOpration):
    def __init__(self):
        BaseOpration.__init__(self)
        self.con = get_redis_connection("massmark")

    def formatter_data_from_ser(self, info):
        """
        用序列化器查询出的数据进行组织
        :param info:
        :return:
        """
        content = dict()
        lnglat = info.get("lnglat")
        content["time"] = info.get("time")
        content["address"] = info.get("address")
        content["category"] = info.get("category__name")
        content["freq"] = info.get("freq")
        return (lnglat, content)

    def formmater_data(self, info):
        """
        处理数据
        :param content:
        :return:
        """
        content = dict()
        lnglat = info.get("lnglat")
        content["time"] = info.get("time")
        content["address"] = info.get("address")
        content["category"] = info.get("category").name
        content["freq"] = info.get("freq")
        return (lnglat, content)

    def get_for_view(self):
        """
        为首页websocket组织数据
        :return:
        """
        content = list()
        keys = self.get_keys()
        if len(keys) is 0:
            return content
        else:
            for key in keys:
                info = dict()
                info["lnglat"] = key.split(",")
                data = self.list_get(key)
                data = list(map(lambda info: json.loads(info), data))
                info["address"] = list(map(lambda info: info.pop("address"), data))[0]
                info["id_count"] = len(data)
                info["data"] = data
                content.append(info)
        return content


class broadcastOp(BaseOpration):
    def __init__(self):
        BaseOpration.__init__(self)
        self.con = get_redis_connection("broadcast")

    def formatter_scroll_info(self, info):
        """
        格式化轮播表数据
        :param info:
        :return:
        """
        content = list()
        content.append(info.get("time"))
        content.append(info.get("freq"))
        content.append(info.get("category").name)
        content.append(info.get("address"))
        return content

    def formatter_heatmap_info(self, info):
        """
        格式化热力图数据
        :param info:
        :return:
        """
        content = dict()
        content["time"] = info.get("time")
        lnglat = info.get("lnglat").split(",")
        content["lng"] = lnglat[0]
        content["lat"] = lnglat[1]
        content["count"] = 1
        return content

    def formatter_scroll_info_from_ser(self, info):
        """
        格式化轮播表数据，数据来源为序列化器
        :param info:
        :return:
        """
        content = list()
        content.append(info.get("time"))
        content.append(info.get("freq"))
        content.append(info.get("category__name"))
        content.append(info.get("address"))
        return content


class chartOp(BaseOpration):
    def __init__(self):
        BaseOpration.__init__(self)
        self.con = get_redis_connection("chart")


class whdisOp(BaseOpration):
    def __init__(self):
        BaseOpration.__init__(self)
        self.con = get_redis_connection("whdis")


class MobListOp(BaseOpration):
    def __init__(self):
        BaseOpration.__init__(self)
        self.con = get_redis_connection("mob-list")
        self.mob = serMobile()

    def get_mob_list(self):
        """
        获取合法手机id列表
        :return:
        """
        result = self.kv_get("mob-list")
        if result == "no this key":
            mob_list = self.mob.get_mobile_list()
            result = mob_list
            self.kv_set("mob-list", mob_list)
        return result

    def update_mob_list(self):
        mob_list = self.mob.get_mobile_list()
        self.kv_set("mob-list", mob_list)


class ObjectOp(BaseOpration):
    def __init__(self):
        BaseOpration.__init__(self)
        self.con = get_redis_connection("object")
        self.mob = serMobile()

    def get_mob_list(self):
        """
        获取合法手机id列表
        :return:
        """
        result = self.kv_get("mob-list")
        if result == "no this key":
            mob_list = self.mob.get_mobile_list()
            result = mob_list
            self.kv_set("mob-list", mob_list)
        return result

    def update_mob_list(self):
        mob_list = self.mob.get_mobile_list()
        self.kv_set("mob-list", mob_list)
