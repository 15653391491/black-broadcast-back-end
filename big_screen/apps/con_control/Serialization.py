import logging
import datetime

from pymysql import IntegrityError

from .models import MobileInfo, District, MonitorInfo, MobileUseRecord, MobileNewLocation
from big_screen.utils import sys_setting as code
from big_screen.utils.box import Serialization as ser

errlog = logging.getLogger("Process")


class serMobile(ser.SerTable):
    def __init__(self):
        """
        设备表序列化
        """
        ser.SerTable.__init__(self)
        self.table = MobileInfo.objects

    def is_mobile_exit(self, mobile):
        try:
            self.table.get(mobile=mobile)
        except MobileInfo.DoesNotExist:
            return False
        else:
            return True

    def insert_info(self, *args, **kwargs):
        """
        添加设备
        :param args:
        :param kwargs:
        :return:
        """

        district = kwargs.get("district")
        if district is "0":
            kwargs["district"] = code.SYS_DISTRICT
        try:
            obj = self.table.get(mobile=kwargs.get("mobile"))
        except MobileInfo.DoesNotExist:
            try:
                obj = self.table.create(**kwargs)
                obj.save()
            except IntegrityError:
                con = {"code": code.STATUSCODE_UNSUCCESS, "msg": "添加失败"}
            else:
                con = {"code": code.STATUSCODE_SUCCESS, "msg": "添加成功"}
        else:
            obj.is_delete = 0
            obj.name = kwargs.get("name")
            obj.phonenumber = kwargs.get("phonenumber")
            obj.district = kwargs.get("district")
            obj.save()
            con = {"code": code.STATUSCODE_SUCCESS, "msg": "添加成功"}
        return con

    def update_info(self, update_dict):
        """
        修改设备信息
        :param update_dict:
        :return:
        """
        if "id" in update_dict.keys():
            district = update_dict.get("district")
            if district is "0":
                update_dict["district"] = code.SYS_DISTRICT
            try:
                self.table.filter(id=update_dict.get("id")).update(**update_dict)
            except Exception as e:
                errlog.info(repr(e))
                con = {
                    "code": code.STATUSCODE_UNSUCCESS,
                    "msg": "更新失败"
                }
            else:
                con = {
                    "code": code.STATUSCODE_SUCCESS,
                    "msg": "修改成功"
                }
        else:
            con = {
                "code": code.STATUSCODE_UNSUCCESS,
                "msg": "无关键信息"
            }
        return con

    def get_info(self):
        _query = self.table.filter(is_delete=0).values("id", "district", "mobile", "name",
                                                       "phonenumber", "time")
        content = list(_query)
        content = list(map(self.formatter_foreign_content, content))
        content = self.formatter_content(content)
        return content

    def get_info_list(self):
        _query = self.table.filter(is_delete=False).values("name", "mobile")
        content = list(_query)
        return content

    def delete_info(self, delete_dict):
        """
        :param delete_dict:
        :return:
        """
        if "id" in delete_dict.keys():
            obj = self.table.get(id=delete_dict.get("id"))
            obj.is_delete = True
            obj.save()
            return {"code": code.STATUSCODE_SUCCESS, "msg": "删除成功"}
        else:
            return {"code": code.STATUSCODE_UNSUCCESS, "msg": "无关键信息"}

    def select_info(self, select_dict):
        if type(select_dict) is not dict:
            return {"code": code.STATUSCODE_UNSUCCESS, "msg": "参数必须为一个字典"}
        keys = select_dict.keys()
        if 'mobile' in keys:
            mobile = select_dict.get("mobile")
            _query = self.table.filter(mobile=mobile).values()
        else:
            return "no"
        content = self.formatter_content(list(_query))
        return content


class serUserRecord(ser.SerTable):
    def __init__(self):
        """
        使用记录序列化
        """
        ser.SerTable.__init__(self)
        self.table = MobileUseRecord.objects
        self._query = self.table.all().values()

    def get_info(self):
        _query = self.table.all().values("id", "mobile__name", "monitor__name", "time")
        content = list(_query)
        content = self.formatter_content(content)
        return content

    def select_info(self, select_dict):
        """
        根据时间、设备、检测人员检索打卡记录
        :param select_dict:
        :return:
        """
        keys = select_dict.keys()
        _query = self._query
        if "s_time" in keys and "e_time" in keys:
            s_time = datetime.datetime.strptime(select_dict["s_time"], code.DATA_FORMATTER)
            e_time = datetime.datetime.strptime(select_dict["e_time"], code.DATA_FORMATTER)
            _query = _query.filter(time__gte=s_time, time__lte=e_time)
        if "mobile" in keys:
            mobile = select_dict.get("mobile")
            if mobile is not "0":
                _query = _query.filter(mobile__mobile=mobile).order_by("-time")
        if "idcard" in keys:
            idcard = select_dict.get("idcard")
            if idcard is not "0":
                _query = _query.filter(monitor__idcard=idcard)
        content = self.formatter_content(list(_query))
        content = list(map(self.formatter_foreign_content, content))
        return content

    def formatter_foreign_content(self, content):
        """
        专用外键格式转换器
        :param content:
        :return:
        """
        keys = content.keys()
        if "mobile_id" in keys:
            content["mobile"] = self.mob.get(id=content.pop("mobile_id")).name
        if "monitor_id" in keys:
            content["monitor"] = self.mon.get(id=content.pop("monitor_id")).name
        return content


class serMonitor(ser.SerTable):
    def __init__(self):
        """
        监测人员表序列化
        """
        ser.SerTable.__init__(self)
        self.table = MonitorInfo.objects
        self.mob = MobileInfo.objects

    def get_info_userecord(self):
        content = list(self.table.filter(is_delete=0).values())
        content = self.formatter_content(content)
        content = list(map(self.formatter_foreign_content, content))
        return content

    def get_info(self):
        content = list(self.table.filter(is_delete=0).values())
        content = self.formatter_content(content)
        content = list(map(self.formatter_foreign_content, content))
        return content

    def get_by_mobile(self, mobile):
        dis = self.mob.get(mobile=mobile).district
        content = list(self.table.filter(is_delete=0, district=dis).values())
        content = self.formatter_content(content)
        return content

    def get_info_list(self):
        _query = self.table.all().values("name", "idcard")
        content = list(_query)
        return content

    def delete_info(self, delete_dict):
        """

        :param delete_dict:
        :return:
        """
        if "id" in delete_dict.keys():
            obj = self.table.get(id=delete_dict.get("id"))
            obj.is_delete = 1
            obj.save()
            return {"code": code.STATUSCODE_SUCCESS, "msg": "删除成功"}
        else:
            return {"code": code.STATUSCODE_UNSUCCESS, "msg": "无关键信息"}

    def insert_info(self, *args, **kwargs):
        try:
            obj = self.table.get(idcard=kwargs.get("idcard"))
        except MonitorInfo.DoesNotExist:
            try:
                obj = self.table.create(**kwargs)
                obj.save()
            except IntegrityError:
                con = {"code": code.STATUSCODE_UNSUCCESS, "msg": "添加失败"}
            except Exception:
                con = {"code": code.STATUSCODE_UNSUCCESS, "msg": "添加失败"}
            else:
                con = {"code": code.STATUSCODE_SUCCESS, "msg": "添加成功"}
        else:
            obj.is_delete = 0
            obj.save()
            con = {"code": code.STATUSCODE_SUCCESS, "msg": "添加成功"}
        return con


class serDistrict(ser.SerTable):
    def __init__(self):
        """
        区域表序列化
        """
        ser.SerTable.__init__(self)
        self.table = District.objects

    def get_info_list(self):
        """
        获取本区域下所有地区列表
        :return:
        """
        # -------------------------- 数据准备 -------------------------------
        info_list = list()  # 信息列表

        base_district = code.CHONGQING  # 一级
        sub_district_list = list()  # 二级
        # --------------------------- 一级 ------------------------------------
        info = self.table.filter(id=base_district).values("name")[0]
        info_list.append(info.get("name"))
        # --------------------------- 二级 -------------------------------------
        sub_info = self.table.filter(superior=base_district).values("name", "id")
        for sub in list(sub_info):
            info_list.append(sub.get("name"))
            sub_district_list.append(sub.get("id"))
        # --------------------------- 三级 ---------------------------------------
        for sub_district in sub_district_list:
            sub_sub_info = self.table.filter(superior=sub_district).values("name", "id")
            for sub in list(sub_sub_info):
                info_list.append(sub.get("name"))
        # --------------------------- 返回 -------------------------------------------
        return info_list


class serMobileNewLocation(ser.SerTable):
    def __init__(self):
        """
        路径记录表序列化
        """
        ser.SerTable.__init__(self)
        self.table = MobileNewLocation.objects
        self.mob = MobileInfo.objects

    def get_info(self):
        _query = self.table.all().values("id", "mobile__name", "lnglat", "time")
        content = self.formatter_content(list(_query))
        return content

    def select_info(self, select_dict):
        """
        根据时间检索某台设备的工作路径
        :param select_dict:
        :return:
        """
        # ------------- 查询集 ------------------
        _query = self.table.all().values("lnglat").order_by("time")
        # ------------- 条件过滤 ----------------
        keys = select_dict.keys()
        if "s_time" in keys and "e_time" in keys:
            s_time = datetime.datetime.strptime(select_dict.get("s_time"), code.DATA_FORMATTER)
            e_time = datetime.datetime.strptime(select_dict.get("e_time"), code.DATA_FORMATTER)
            _query = _query.filter(time__gte=s_time, time__lte=e_time)
        if "mobile" in keys:
            mobile = self.mob.get(mobile=select_dict.get("mobile")).id
            _query = _query.filter(mobile__id=mobile)
        # ------------ 结果处理 -------------------
        content = self.formatter_content(list(_query))
        content = list(map(lambda con: con.get("lnglat"), content))
        # ---------------- 返回 --------------------
        return content

