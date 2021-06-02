"""
系统初始化
"""
import traceback
from big_screen.serialization.allSerialization import serMobile, serMonitor, serWhiteCategory, serWhiteList, \
    serDistrict, serBlackCategory
from big_screen.utils.turn_format import time_formatter
from big_screen.utils import sys_setting as code
from big_screen.utils import tools as t
from big_screen.utils import re_format as f


class start_sys:
    def __init__(self):
        self.mob = serMobile()
        self.tf = time_formatter()
        self.md = t.MakeDistrict()
        self.mon = serMonitor()
        self.time = self.tf.now_time_str
        self.wh = serWhiteList()
        self.dis = serDistrict()
        self.bc = serBlackCategory()

    def init_monitor(self):
        """
        增加未知人员
        :return:
        """
        # 默认身份证
        idcard = f.UNKNOW_IDCARD
        # 默认未知区域
        try:
            dis_id = self.mob.dis.get(adcode=code.UNKNOW).id
        except self.mob.dis.model.DoesNotExist:
            self.init_district()
            dis_id = self.mob.dis.get(adcode=code.UNKNOW).id
        try:
            self.mon.table.get(idcard=idcard)
        except self.mon.table.model.DoesNotExist:
            insert_dict = dict()
            insert_dict["idcard"] = idcard
            insert_dict["name"] = "none"
            insert_dict["district"] = dis_id
            insert_dict["is_delete"] = 1
            insert_dict["time"] = self.time
            self.mon.insert_info(**insert_dict)

    def init_mobile(self):
        """
        增加未知手机
        :return:
        """
        # ---------- 组织数据 ------------
        mobile = f.UNKNOW_MOBILE
        is_delete = 1
        try:
            dis_id = self.mob.dis.get(adcode=code.UNKNOW).id
        except self.mob.dis.model.DoesNotExist:
            self.init_district()
            dis_id = self.mob.dis.get(adcode=code.UNKNOW).id
        # ------------------------------------
        try:
            self.mob.table.get(mobile=mobile)
        except self.mob.table.model.DoesNotExist:
            insert_dict = dict()
            insert_dict["mobile"] = mobile
            insert_dict["is_delete"] = is_delete
            insert_dict["time"] = self.time
            insert_dict["district"] = dis_id
            self.mob.insert_info(**insert_dict)
    def init_district(self):
        """
        增加未知区域，增加省市县三级行政区(本地)
        :return:
        """
        # ---------- 情况数据表 ----------------
        self.dis.table.all().delete()
        # ------------ 加入未知区域 -------------
        self.md.unknow_district()
        # ------------ 加入一级行政区 ------------
        self.md.province_district()
        # ------------ 加入二级行政区 ------------
        self.md.city_district(code.SYS_DISTRICT)
        try:
            # ------------ 加入三级行政区 ------------
            self.md.dis_district(code.SYS_DISTRICT)
        except Exception:
            pass
        # ---------------- 加入台站 ---------------------
        self.md.tg_district(code.SYS_DISTRICT)

    def init_whcategory(self):
        """
        初始化白名单种类
        :return:
        """
        # ----------- 清空表 ---------------
        wc = serWhiteCategory()
        wc.table.all().delete()
        # ------------ 插入种类 --------------
        for i in range(len(f.WHITE_TYPE)):
            insert_dict = f.WHITE_TYPE[i]
            insert_dict["id"] = i + 1
            wc.insert_info(**insert_dict)

    def init_whitelist(self):
        """
        初始化白名单，添加一个未知白名单,频点为0
        :return:
        """
        # --------------- 清空白名单表 -----------------
        # self.wh.table.all().delete()
        # --------------- 未知白名单 ------------------
        insert_dict = dict()
        insert_dict["freq"] = 0
        insert_dict["name"] = "none"
        insert_dict["time"] = self.time
        insert_dict["type"] = 4
        insert_dict["district"] = self.dis.table.get(adcode=f.UNKNOW_DISTRICT).id
        # --------------- 加入数据库 ---------------------
        self.wh.insert_info(insert_dict)

    def init_blackcategory(self):
        """
        黑广播种类初始化
        :return:
        """
        # ----------------- 清空表 --------------------
        self.bc.table.all().delete()
        # ------------ 初始化数据 ---------------------
        for i in range(len(f.BC_TYPE)):
            insert_dict = dict()
            insert_dict["id"] = i + 1
            insert_dict["name"] = f.BC_TYPE[i]
            insert_dict["time"] = self.time
            insert_dict["num"] = i + 1
            self.bc.insert_info(**insert_dict)

    def start(self):
        # self.init_district()
        self.init_whcategory()
        self.init_blackcategory()

    def start2(self):
        self.init_mobile()
        self.init_monitor()
        self.init_whitelist()