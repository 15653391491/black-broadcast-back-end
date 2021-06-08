import datetime
import logging
from django.db.models.manager import Manager
from django.db.utils import IntegrityError
import os

from big_screen.utils import sys_setting as code
from con_control.models import MobileInfo, MonitorInfo, District
from big_screen.utils import re_format as f

errlog = logging.getLogger("Process")


class SerTable:
    def __init__(self):
        self.table = Manager
        self.mob = MobileInfo.objects
        self.dis = District.objects
        self.mon = MonitorInfo.objects

    def get_id_list(self):
        """
        返回id列表
        :return:
        """
        content = list(self.table.all().values("id", "name"))
        return content

    def get_info(self, *args):
        """
        获取表数据
        :return:
        """
        content = list(self.table.all().values())
        content = self.formatter_content(content)
        return content

    def get_info_select(self):
        """
        获取下拉框列表
        :return:
        """
        content = list(self.table.all().values("name", "num"))
        content = self.formatter_content(content)
        return content

    def get_info_list(self):
        """
        获取一个名单
        :return:
        """
        info_list = self.table.all().values("name")
        content = list()
        for info in list(info_list):
            content.append(info.get("name"))
        return content

    def select_info(self, select_dict):
        """
        检索表数据,没检索到返回None
        :param select_dict:
        :return:
        """
        # if type(select_dict) is not dict:
        #     return {"code": code.STATUSCODE_UNSUCCESS, "msg": "参数必须为一个字典"}
        keys = select_dict.keys()
        _query = list()
        if "s_time" in keys and "e_time" in keys:
            s_time = datetime.datetime.strptime(select_dict["s_time"], code.DATA_FORMATTER)
            e_time = datetime.datetime.strptime(select_dict["e_time"], code.DATA_FORMATTER)
            _query = self.table.filter(time__gte=s_time, time__lte=e_time).values()
        if "id" in keys:
            _id = eval(select_dict["id"])
            if type(_id) is not int:
                return {"code": code.STATUSCODE_UNSUCCESS, "msg": "id必须为正整数"}
            _query = self.table.filter(id=_id).values()
        if "mobile" in keys:
            mobile = select_dict.get("mobile")
            _query = self.table.filter(mobile__mobile=mobile).values()
        if "adcode" in keys:
            adcode = select_dict.get("adcode")
            if type(adcode) is list:
                adcode = adcode[0]
            _query = self.table.filter(adcode=adcode).values()
        content = self.formatter_content(list(_query))
        return content

    # def insert_info(self, insert_dict):
    def insert_info(self, *args, **kwargs):
        # def insert_info(self,**kwargs):
        """
        加入表数据
        :return:
        """
        try:
            obj = self.table.create(**kwargs)
            obj.save()
        except IntegrityError as e:
            raise e
        else:
            con = {"code": code.STATUSCODE_SUCCESS, "msg": "添加成功"}
        return con

    def delete_info(self, delete_dict):
        """
        删除表数据
        :param delete_dict:
        :return:
        """
        if "id" in delete_dict.keys():
            self.table.get(id=delete_dict.get("id")).delete()
            return {"code": code.STATUSCODE_SUCCESS, "msg": "删除成功"}
        else:
            return {"code": code.STATUSCODE_UNSUCCESS, "msg": "无关键信息"}

    def update_info(self, update_dict):
        """
        更改表数据
        :param update_dict:
        :return:
        """
        if "id" in update_dict.keys():
            try:
                self.table.filter(id=update_dict.get("id")).update(**update_dict)
            except Exception as e:
                raise e
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

    def formatter_content(self, content):
        result = list()
        for con in content:
            keys = con.keys()
            if "time" in keys:
                con["time"] = datetime.datetime.strftime(con["time"], code.DATA_FORMATTER)
            if "record" in keys:
                con["record"] = "/m/" + con["record"]
            if "mobile" in keys:
                if type(con["mobile"]) is not str:
                    con["mobile"] = con["mobile"].mobile
            # 判断音频文件是否存在
            record = con["record"]
            if record != None:
                record = record.split("/")[2]
                recordName = code.file_DIR + "/" + record
                con["recordExist"] = os.path.exists(recordName)
            result.append(con)
        return result

    def formatter_foreign_content(self, content):
        """

        :param content:
        :return:
        """
        keys = content.keys()
        if "mobile" in keys:
            try:
                content["mobile"] = self.mob.get(mobile=content.get("mobile"))
            except MobileInfo.DoesNotExist as e:
                raise e
        if "district" in keys:
            try:
                content["district_num"] = content.get("district")
                content["district"] = self.dis.get(id=content.get("district")).name
            except self.dis.model.DoesNotExist:
                content["district_num"] = f.UNKNOW_DISTRICT
                content["district"] = self.dis.get(adcode=f.UNKNOW_DISTRICT).name
        return content
