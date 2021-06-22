import logging

from con_control.models import District, MobileInfo
from .models import WhiteList, WhiteListCategory
from big_screen.utils import sys_setting as code, tools as t
from big_screen.utils.box import Serialization as ser
from big_screen.utils import re_format as f

errlog = logging.getLogger("Process")


class serWhiteList(ser.SerTable):
    def __init__(self):
        ser.SerTable.__init__(self)
        self.table = WhiteList.objects
        self.mobile = MobileInfo.objects
        self.dis = District.objects
        self.unknow_dis = self.dis.filter(adcode=f.UNKNOW_DISTRICT)[0].id  # 未知区域id
        self.sys_dis = self.dis.get(adcode=code.SYS_DISTRICT).id

    def get_info(self, mobile):
        _query = self.table.all().values()
        if mobile is "111111111111111":
            content = list(_query)
        else:
            # ------------------ 通用白名单 ----------------
            nomal_content = list(_query.filter(district=code.SYS_DISTRICT).values())
            # ------------------ 区域白名单 ----------------
            dis_id = self.mobile.get(mobile=mobile).district
            dis_obj = self.dis.get(id=dis_id)
            district_content = list(_query.filter(district=dis_obj.superior).values())
            # ----------------- 台站白名单 ------------------
            tg_content = list(_query.filter(district=dis_id).values())
            content = nomal_content + district_content + tg_content
        content = self.formatter_content(content)
        content = list(map(self.formatter_foreign_content, content))
        return content

    def insert_info(self, mobile, insert_dict):
        """
        数据来源于设备的话不允许插入普通头白名单,一律默认为区域白名单 区域根据设备id获得
        :param mobile:
        :param insert_dict:
        :return:
        """
        # --------- 判断数据来源 ----------
        keys = insert_dict.keys()
        if "district" in keys:  # 来自于后端
            dis = insert_dict.get("district")
            if dis is "0":
                dis = code.SYS_DISTRICT
                insert_dict["district"] = dis
            insert_dict["freq"] = t.freq_interface_to_sql(insert_dict.get("freq"))
        else:  # 来自于设备
            dis = self.mobile.get(mobile=mobile).district
            insert_dict["district"] = dis
            insert_dict["time"] = t.get_time(insert_dict.get("time"))
            insert_dict.pop("location")
            insert_dict.pop("user")
            if insert_dict["type"] is "1":
                insert_dict["type"] = "3"
        # ----------- 判断该白名单是否已存在 ------------
        freq = insert_dict.get("freq")
        count = len(list(self.table.filter(freq=freq, district=dis)))
        if count is not 0:
            return {"code": code.STATUSCODE_UNSUCCESS, "msg": "重复"}
        # ---------- 插入白名单 -----------
        obj = self.table.create(**insert_dict)
        obj.save()
        # ---------- 返回 -----------------
        return code.con

    def get_info_by_category(self, mobile):
        """
        根据种类获取白名单
        :return: 
        """
        _query = self.table.filter(district=code.CHONGQING).values("category", "freq")
        content = list(_query)
        info = dict()
        for con in content:
            if str(con.get("category")) in info.keys():
                info[str(con.get("category"))].append(con.get("freq"))
            else:
                info[str(con.get("category"))] = list()
                info[str(con.get("category"))].append(con.get("freq"))
        return info

    def update_info(self, update_dict):
        """
        修改白名单的名称、所属地区
        :param update_dict:
        :return:
        """
        try:
            wh_id = update_dict.get("id")
            wh_dis = update_dict.get("district")
        except Exception as e:
            raise e
        if wh_dis is self.unknow_dis:
            update_dict["district"] = self.sys_dis
        try:
            self.table.get(id=wh_id).update(**update_dict)
        except self.table.model.DoesNotExist as e:
            raise e
        except Exception as e:
            raise e


class serWhiteCategory(ser.SerTable):
    def __init__(self):
        ser.SerTable.__init__(self)
        self.table = WhiteListCategory.objects
