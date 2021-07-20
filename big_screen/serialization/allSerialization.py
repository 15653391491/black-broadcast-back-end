import datetime
import logging

from django.db.models import Count
from pymysql import IntegrityError

from big_screen.utils import re_format as f
from big_screen.utils import sys_setting as code, tools as t
from big_screen.utils import turn_format as tf
from big_screen.utils.turn_format import freq_formatter
from con_brocast.models import BlackRecord, BlackCategory
from con_control.models import MonitorInfo, MobileInfo, MobileNewLocation, MobileUseRecord, District
from mobile.models import MobileVersion, RedioTest
from version.models import MobileToPlatformInfo, PlatformInfo
from whiteList.models import WhiteList, WhiteListCategory
from .baseSerialization import SerTable

errlog = logging.getLogger("Process")


class serBlackCategory(SerTable):
    def __init__(self):
        SerTable.__init__(self)
        self.table = BlackCategory.objects

    def make_bc(self):
        """
        修正黑广播种类表
        :return:
        """
        bc_type = f.BC_TYPE
        update_dict = dict()
        for i in range(len(bc_type)):
            update_dict["id"] = str(i + 1)
            update_dict["name"] = bc_type[i]
            update_dict["num"] = str(i + 1)
            self.update_info(update_dict)


class serBlackRecord(SerTable):
    def __init__(self):
        SerTable.__init__(self)
        self.table = BlackRecord.objects
        self.wh = t.GetWhiteList()
        self.wh_region = t.GetWhiteList("1")
        self.bc = BlackCategory.objects

    # --------------------- 增删查改 ----------------------
    def get_info(self):
        """
        获取黑广播信息
        :return:
        """
        _query = self.table.filter(islegal=0).values("id", "time", "freq", "lnglat", "category__name", "mobile__name",
                                                     "record",
                                                     "address",
                                                     "contact", "monitor", "common", "category__num",
                                                     "mobile__id").order_by(
            "-time")
        # ------------------------ 格式化结果 ------------------------------
        contant = self.formatter_content(list(_query))
        return contant

    def select_info(self, select_dict):
        # ------------------------------------------------ 查询条件 -----------------------------------------------
        keys = select_dict.keys()
        select_info = dict()
        if "s_time" in keys:
            select_info["time__gte"] = select_dict.get("s_time")
        if "e_time" in keys:
            select_info["time__lte"] = select_dict.get("e_time")
        if "category" in keys:
            category = select_dict["category"]
            if category is not "0":
                select_info["category__num"] = select_dict.get("category")
        if "mobile" in keys:
            mobile = select_dict["mobile"]
            if mobile is not "0":
                select_info["mobile__id"] = select_dict.get("mobile")
        if "freq" in keys:
            freq = select_dict["freq"]
            if freq is not "0" and freq is not "":
                select_info["freq"] = select_dict.get("freq")
        if "district" in keys:
            select_info["district"] = select_dict.get("district")
        select_info["islegal"] = 0
        query = self.table.filter(**select_info).values("id", "time", "freq", "lnglat", "category__name",
                                                        "mobile__name",
                                                        "record",
                                                        "address",
                                                        "contact", "common", "category__num", "mobile__id",
                                                        "islegal").order_by(
            "-time")
        contant = self.formatter_content(list(query))
        return contant

    def select_for_heatmap(self, select_dict):
        """
        检索结果为热力图数据
        :param select_dict:
        :return:
        """
        # ------------------------------------------------ 查询集 -------------------------------------------------
        _query = self.table.filter(islegal=0).values("lnglat").order_by("-time")
        # ------------------------------------------------ 查询条件 -----------------------------------------------
        keys = select_dict.keys()
        if "s_time" in keys and "e_time" in keys:
            s_time = select_dict["s_time"]
            e_time = select_dict["e_time"]
            _query = _query.filter(time__gte=s_time, time__lte=e_time)
        contant = list()
        for obj in list(_query):
            lnglat = obj.get("lnglat").split(",")
            info = dict()
            info["lng"] = lnglat[0]
            info["lat"] = lnglat[1]
            info["count"] = 1
            contant.append(info)
        return contant

    def select_obj(self, select_dict):
        """
        返回查询集
        :param select_dict:
        :return:
        """
        # _query = self.table.filter(islegal=0).order_by("-time")
        select_info = dict()
        select_info["islegal"] = 0
        keys = select_dict.keys()
        if "s_time" in keys and "e_time" in keys:
            select_info["time__gte"] = select_dict.get("s_time")
            select_info["time__lte"] = select_dict.get("e_time")
        _query = self.table.filter(**select_info).order_by("-time")
        return _query

    def update_info(self, update_dict):
        """
        更新黑广播
        :param update_dict:
        :return:
        """
        wc = serWhiteCategory()
        if "id" in update_dict.keys():
            category = update_dict.get("category")
            if category == "0":
                update_dict["category"] = wc.table.get(id=f.UNKNOW_WHITECATEGORY).id
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

    def get_info_obj(self):
        """
        经过白名单过滤,获取查询集
        :return:
        """
        query = self.table.all().values("id", "time", "freq", "lnglat", "category__name", "mobile__name", "record",
                                        "address",
                                        "contact", "common","islegal").order_by("-time").exclude(islegal=1)
        return query

    # ----------------- 数据修正 ----------------------
    def make_freq(self):
        """
        修正数据库中的频点 *10后改为正常
        :return:
        """
        ff = tf.freq_formatter()
        query = self.table.all()

        for info in query:
            freq = info.freq
            if ff.isFreqLegal(freq):
                continue
            freq = ff.mobile_to_django(freq)
            # print(info.freq)
            info.freq = freq
            info.mobile_id = 93
            info.save()

    def make_district(self):
        """
        修正数据库中黑广播所属区域
        :return:
        """
        query = self.table.all()
        for con in query:
            lnglat = con.lnglat
            adcode = t.getaddress(lnglat).get("adcode")
            try:
                dis_id = self.dis.get(adcode=adcode, is_district=1).id
            except self.dis.model.DoesNotExist:
                dis_id = f.UNKNOW_DISTRICT
            con.district = dis_id
            con.mobile_id = 93
            con.save()

    def make_islegal(self):
        """
        重新计算广播信息是否合法
        :return:
        """
        wh = serWhiteList()
        query = self.table.all()
        for obj in query:
            freq = obj.freq
            district = obj.district
            try:
                wh_legal = wh.is_freqLegal_in_dis(freq, district)
            except Exception:
                wh_legal = False
            if wh_legal:
                obj.islegal = 1
            else:
                obj.islegal = 0
            obj.save()

    def make_bc(self, s, e):
        """
        修正黑广播种类
        交换s,e
        :return:
        """
        query = self.table.all()  # 查询集
        curr = self.bc.get(id=s)  # 当前
        changeTo = self.bc.get(id=e)  # 交换为
        for obj in query:
            if obj.category == curr:
                obj.category = changeTo
                obj.save()
            if obj.category == changeTo:
                obj.category = curr
                obj.save()

    def make_blackCategory(self):
        """
        使用make_bc()函数，全部替换
        :return:
        """
        self.make_bc(1, 2)
        self.make_bc(2, 4)
        self.make_bc(4, 6)
        self.make_bc(5, 4)

    def makeReportMonitor(self):
        query = self.table.all()
        ur = serUserRecord()
        for info in query:
            mob_id = info.mobile.id
            time = info.time
            record_obj = ur.getReportMonitor(mob_id, time)
            info.monitor = record_obj.get("monitor")
            info.save()

    # ------------------- 统计 ---------------------
    def count_by_category(self, select_dict):
        """
        根据时间进行种类统计
        :param select_dict:
        :return:
        """
        s_time = datetime.datetime.strptime(select_dict.get("start"), code.DATA_FORMATTER)
        e_time = datetime.datetime.strptime(select_dict.get("end"), code.DATA_FORMATTER)
        # ------------------------- 查询集 -------------------------------------------
        bro_info = self.table.filter(time__gte=s_time, time__lte=e_time).exclude(lslegal=1)
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

    def summaryByRegion(self):
        summaryResurt = self.table.filter(islegal=0).values("district").annotate(count=Count("district")).order_by(
            "-count")
        for info in summaryResurt:
            info["district"] = self.dis.get(id=info.get("district")).name
        return self.queryToList(summaryResurt)

    #  -------------- 组织数据 -------------------
    def organizeScroll(self, query):
        """
        轮播表数据
        :param query:
        :return:
        """
        query = query.values("time", "freq", "category__name", "address")
        ret = map(self.formatterScroll, query)
        return [info for info in ret]

    def organizeMassMark(self, query):
        """
        海量点数据
        :param query:
        :return:
        """
        query = query.values("time", "freq", "category__name", "address", "lnglat")
        ret = map(self.formatterMassMark, query)
        return [info for info in ret]

    def organizeHeatMap(self, query):
        """
        热力图数据
        :param query:
        :return:
        """
        query = query.values("time", "lnglat")
        ret = map(self.formatterHeatMap, query)
        return [info for info in ret]

    # ------------- 格式转化 -------------------
    def formatterScroll(self, info):
        """
        轮播表格式
        :param info:
        :return:
        """
        time = info.get("time")
        time = time.strftime(code.DATA_FORMATTER)
        freq = info.get("freq")
        category = info.get("category__name")
        address = info.get("address")
        return [time, freq, category, address]

    def formatterMassMark(self, info):
        """
        格式化海量点
        :param info:
        :return:
        """
        time = info.get("time")
        time = time.strftime(code.DATA_FORMATTER)
        freq = info.get("freq")
        category = info.get("category__name")
        address = info.get("address")
        lnglat = info.get("lnglat")
        return (lnglat, {
            'freq': freq,
            'category': category,
            'time': time,
            'address': address})

    def formatterHeatMap(self, info):
        """
        格式化海量点
        :param info:
        :return:
        """
        time = info.get("time")
        time = time.strftime(code.DATA_FORMATTER)
        lnglat = info.get("lnglat").split(",")
        lng = lnglat[0]
        lat = lnglat[1]
        return {
            'lng': lng,
            'count': 1,
            'time': time,
            'lat': lat}


class serMobile(SerTable):
    def __init__(self):
        """
        设备表序列化
        """
        SerTable.__init__(self)
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
            kwargs["district"] = self.dis.get(adcode=code.SYS_DISTRICT, is_district=1).id
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
            con = {"code": code.STATUSCODE_SUCCESS, "msg": "已添加"}
        return con

    def update_info(self, update_dict):
        """
        修改设备信息
        :param update_dict:
        :return:
        """
        if "id" in update_dict.keys():
            mob_id = update_dict.get("id")
            mob_obj = self.table.get(id=mob_id)
            # ************ 未知手机 **************
            if mob_obj.mobile != f.UNKNOW_MOBILE:
                district = update_dict.get("district")
                if district == "0":
                    update_dict["district"] = self.dis.get(adcode=code.SYS_DISTRICT, is_district=1).id
                try:
                    self.table.filter(id=update_dict.get("id")).update(**update_dict)
                except Exception:
                    con = {
                        "code": code.STATUSCODE_UNSUCCESS,
                        "msg": "修改失败"
                    }
                    return con
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

    def get_info_select(self):
        """
        获取下拉框的信息
        :return:
        """
        query = self.table.filter(is_delete=0).values("id", "name")
        content = list()
        for con in list(query):
            info = dict()
            info["value"] = str(con.get("id"))
            info["label"] = con.get("name")

            content.append(info)
        content = list(map(self.formatter_foreign_content, content))
        content = self.formatter_content(content)
        return content

    def get_info(self):
        _query = self.table.filter(is_delete=0).values("id", "district", "mobile", "name",
                                                       "phonenumber", "time")
        content = list(_query)
        content = list(map(self.formatter_foreign_content, content))
        content = self.formatter_content(content)
        return content

    def get_mobile_list(self):
        """
        获取注册过，且未删除的手机id
        :return:
        """
        query = self.table.filter(is_delete=0)
        content = list()
        for obj in query:
            content.append(obj.mobile)
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
            obj.is_delete = 1
            obj.save()
            return {"code": code.STATUSCODE_SUCCESS, "msg": "删除成功"}
        else:
            return {"code": code.STATUSCODE_UNSUCCESS, "msg": "无关键信息"}

    def select_info(self, select_dict):
        keys = select_dict.keys()
        query = self.table.filter(is_delete=0).values()
        if "district" in keys:
            query_list = list()
            district = select_dict.get("district")
            if district == "0":
                query_list = list(query)
            else:
                taizhan_query = self.dis.filter(superior=district, is_district=0)
                for tz_obj in taizhan_query:
                    dis_id = tz_obj.id
                    tz_query = query.filter(district=dis_id)
                    query_list.extend(list(tz_query))
        else:
            query_list = list(query)
            # dis_id = self.dis.get(superior=district, is_district=0).id
            # query = query.filter(district=dis_id)
        content = list(map(self.formatter_foreign_content, query_list))
        content = self.formatter_content(content)
        return content


class serUserRecord(SerTable):
    def __init__(self):
        """
        使用记录序列化
        """
        SerTable.__init__(self)
        self.table = MobileUseRecord.objects

    def get_info(self):
        _query = self.table.all().values("id", "mobile__name", "monitor__name", "time", "version").order_by("-time")
        content = list(_query)
        content = self.formatter_content(content)
        return content

    def get_recent_record(self, mob_id):
        """
        通过手机id获取最新记录
        :param mob_id:
        :return:
        """
        query = self.table.filter(mobile=mob_id).values().order_by("-time")
        content = list(map(self.formatter_foreign_content, list(query)))
        if len(content) == 0:
            content = [{"monitor": "none"}]
        return content[0]

    def getReportMonitor(self, mobile):
        """
        通过手机id获取打卡人
        :param mob_id:
        :param time:
        :return:
        """
        mobileId= self.mob.get(mobile=mobile).id
        query = self.table.filter(mobile=mobileId).values().order_by("-time")
        query = [info for info in query]
        content = map(self.formatter_foreign_content, query)
        content = [info for info in content]
        if len(content) == 0:
            content = [{"monitor": ""}]
        return content[0]

    def select_info(self, select_dict):
        """
        根据时间、设备、检测人员检索打卡记录
        :param select_dict:
        :return:
        """
        select_info = dict()
        keys = select_dict.keys()
        if "s_time" in keys and "e_time" in keys:
            select_info["time__gte"] = select_dict.get("s_time")
            select_info["time__lte"] = select_dict.get("e_time")
        if "mobile" in keys:
            select_info["mobile_id"] = select_dict.get("mobile")
        if "monitor" in keys:
            select_info["monitor_id"] = select_dict.get("monitor")
        query = self.table.filter(**select_info).values("id", "mobile__name", "monitor__name", "time",
                                                        "version").order_by("-time")
        content = self.formatter_content(list(query))
        content = list(map(self.formatter_foreign_content, content))
        return content

    def countNum(self):
        """
        统计不同手机的打卡次数
        :return:
        """
        return self.table.values("mobile__name").annotate(count=Count("mobile__name"))

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


class serMonitor(SerTable):
    def __init__(self):
        """
        监测人员表序列化
        """
        SerTable.__init__(self)
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
            try:
                obj = self.table.get(id=delete_dict.get("id"))
                obj.is_delete = 1
                obj.save()
            except self.table.model.DoesNotExist:
                return {"code": code.STATUSCODE_UNSUCCESS, "msg": "无该人员"}
            else:
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
            except IntegrityError as e:
                raise e
                # con = {"code": code.STATUSCODE_UNSUCCESS, "msg": "添加失败"}
            except Exception as e:
                raise e
                # con = {"code": code.STATUSCODE_UNSUCCESS, "msg": "添加失败"}
            else:
                con = {"code": code.STATUSCODE_SUCCESS, "msg": "添加成功"}
        else:
            obj.is_delete = 0
            obj.save()
            con = {"code": code.STATUSCODE_SUCCESS, "msg": "添加成功"}
        return con

    def update_info(self, update_dict):
        """
        更新人员
        :param update_dict:
        :return:
        """
        district = update_dict.get("district")
        if district == "0":
            update_dict["district"] = self.dis.get(adcode=code.SYS_DISTRICT, is_district=1).id
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

    def select_info(self, select_dict):
        """
        检索人员
        :param select_dict:
        :return:
        """
        district = select_dict.get("district")
        content = list()
        if district == "0":
            query = self.table.filter(is_delete=0).values()
            content = list(query)
        else:
            dis_id_list = self.dis.filter(superior=district).values("id")
            for dis_info in list(dis_id_list):
                dis_id = dis_info.get("id")
                query = self.table.filter(is_delete=0, district=dis_id).values()
                content.extend(list(query))
        content = self.formatter_content(content)
        content = list(map(self.formatter_foreign_content, content))
        return content


class serDistrict(SerTable):
    def __init__(self):
        """
        区域表序列化
        """
        SerTable.__init__(self)
        self.table = District.objects

    def get_info_select(self):
        """
        获取二级行政区列表(下拉框用)
        :return:
        """
        sys_dis_id = self.table.get(adcode=code.SYS_DISTRICT, is_district=1).id
        sys_dis_name = self.table.get(adcode=code.SYS_DISTRICT, is_district=1).name
        query = self.table.filter(superior=sys_dis_id, is_district=1).values()
        content = list()
        content.append({"name": sys_dis_name, "num": "0"})
        for info in list(query):
            con = dict()
            con["name"] = info.get("name")
            con["num"] = str(info.get("id"))
            content.append(con)
        return content

    def get_info_select_bak(self):
        """
        获取二级行政区列表(下拉框用)
        :return:
        """
        sys_dis_id = self.table.get(adcode=code.SYS_DISTRICT, is_district=1).id
        sys_dis_name = self.table.get(adcode=code.SYS_DISTRICT, is_district=1).name
        query = self.table.filter(superior=sys_dis_id, is_district=1).values()
        content = list()
        content.append({"label": sys_dis_name, "value": 0})
        for info in list(query):
            con = dict()
            con["label"] = info.get("name")
            con["value"] = info.get("id")
            content.append(con)
        return content

    def get_taizhan_select(self):
        """
        获取台站列表(下拉框用)
        :return:
        """
        sys_dis_name = self.table.get(adcode=code.SYS_DISTRICT, is_district=1).name
        query = self.table.filter(is_district=0).values()
        content = list()
        content.append({"name": sys_dis_name, "num": "0"})
        for info in list(query):
            con = dict()
            con["name"] = info.get("name")
            con["num"] = str(info.get("id"))
            content.append(con)
        return content

    def get_taizhan_select_copy(self):
        """
        获取台站列表(下拉框用)
        :return:
        """
        sys_dis_name = self.table.get(adcode=code.SYS_DISTRICT, is_district=1).name
        query = self.table.filter(is_district=0).values()
        content = list()
        for info in list(query):
            con = dict()
            con["label"] = info.get("name")
            con["value"] = info.get("id")
            content.append(con)
        return content

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

    def get_city_list(self):
        """
        获取二级行政区名单
        :return:
        """
        sys_dis_id = self.table.get(adcode=code.SYS_DISTRICT, is_district=1).id
        content = self.table.filter(superior=sys_dis_id, is_district=1).values("id", "name")
        return list(content)

    def get_district_by_mobile(self, mobile):
        """
        根据手机号获取地区
        :param mobile:
        :return:
        """
        dis_id = self.mob.get(mobile=mobile).district
        dis_obj = self.table.get(id=dis_id)
        info_list = {
            "district": dis_obj.superior,
            "name": dis_obj.name
        }
        return info_list

    def getLevel(self, district):
        return self.table.get(id=district).superior


class serMobileNewLocation(SerTable):
    def __init__(self):
        """
        路径记录表序列化
        """
        SerTable.__init__(self)
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
        select_info = dict()
        # ------------- 条件过滤 ----------------
        keys = select_dict.keys()
        if "s_time" in keys and "e_time" in keys:
            # pass
            select_info["time__gte"] = select_dict.get("s_time")
            select_info["time__lte"] = select_dict.get("e_time")
        if "mobile" in keys:
            mobile = self.mob.get(mobile=select_dict.get("mobile")).id
            select_info["mobile__id"] = mobile
        _query = self.table.filter(**select_info).values("lnglat")
        # ------------ 结果处理 -------------------
        content = self.formatter_content(list(_query))
        content = list(map(lambda con: con.get("lnglat"), content))
        # ---------------- 返回 --------------------
        return content

    def get_recent_time(self, mobile):
        """
        获取该手机最近打卡记录的时间
        :param mobile:
        :return:
        """
        query = self.table.filter(mobile__mobile=mobile).order_by("-time")
        if len(query) > 0:
            obj = query[0]
        else:
            return 0
        time = obj.time
        return time


class serWhiteList(SerTable):
    def __init__(self):
        SerTable.__init__(self)
        self.table = WhiteList.objects
        self.whc = serWhiteCategory()

    def get_info(self):
        query = self.table.all().exclude(freq=f.UNKNOW_WHITELIST).values()
        content = list(query)
        content = self.formatter_content(content)
        content = list(map(self.formatter_foreign_content, content))
        return content

    def get_normal_wh(self):
        """
        获取普通频点
        :return:
        """
        query = self.table.filter(type=1).values("freq")
        content = list(map(lambda info: str(info.get("freq")), list(query)))
        return content

    def insert_info(self, insert_dict):
        """
        插入数据库 同区域下频点不可重复
        :param insert_dict:
        :return:
        """
        freq = insert_dict.get("freq")
        district = insert_dict.get("district")
        freq_type = insert_dict.get("type")
        # 验证频点是否合法
        ff = freq_formatter()
        islegal = ff.isFreqLegal(freq)
        if not islegal:
            return {"code": code.STATUSCODE_UNSUCCESS, "msg": "该频点不合法"}
        # ********** 普通频点 *******************
        sys_district = self.dis.get(adcode=code.SYS_DISTRICT, is_district=1).id
        if str(freq_type) == "1":
            insert_dict["district"] = sys_district
            curr_freq_query = self.table.filter(freq=freq).count()
            if curr_freq_query > 0:
                return {"code": code.STATUSCODE_UNSUCCESS, "msg": "该频点重复"}
        else:
            if district == "0":
                con = code.con_false
                con["msg"] = "请选择其他地区"
                return con
        # ************ 区域频点与普通频点重复 ***************
        nornam_wh = self.get_normal_wh()
        if str(freq) in nornam_wh:
            return {"code": code.STATUSCODE_UNSUCCESS, "msg": "该频点与普通频点重复"}
        # *********** 区域内重复 *****************
        try:
            self.table.get(freq=freq, district=district)
        except self.table.model.DoesNotExist:
            obj = self.table.create(**insert_dict)
            obj.save()
            return {"code": code.STATUSCODE_SUCCESS, "msg": "添加成功"}
        else:
            return {"code": code.STATUSCODE_UNSUCCESS, "msg": "频点在所在区域中重复"}

    def update_info(self, update_dict):
        """
        根据频点id更新分类信息
        :param update_dict:
        :return:
        """
        keys = update_dict.keys()
        if "id" in keys:
            freq_obj = self.table.get(id=update_dict.get("id"))
            freq = freq_obj.freq
            this_dis = freq_obj.district
            district = update_dict.get("district")
            freq_type = update_dict.get("type")
            # 如果修改为普通频点
            if str(freq_type) == "1":
                if self.table.filter(freq=freq).count() > 1:
                    return {"code": code.STATUSCODE_UNSUCCESS, "msg": "频点重复"}
                else:
                    sys_id = self.dis.get(adcode=code.SYS_DISTRICT, is_district=1).id
                    update_dict["district"] = sys_id
                    self.table.filter(id=update_dict.get("id")).update(**update_dict)
                    return {"code": code.STATUSCODE_SUCCESS, "msg": "修改成功"}
            else:
                if district == "0":
                    con = code.con_false
                    con["msg"] = "请选择其他地区　"
                    return con
            if str(this_dis) == str(district):
                update_dict.pop("district")
                self.table.filter(id=update_dict.get("id")).update(**update_dict)
                return {"code": code.STATUSCODE_SUCCESS, "msg": "修改成功"}
            try:
                self.table.get(freq=freq, district=district)
            except self.table.model.DoesNotExist:
                if district == "0":
                    update_dict["district"] = self.dis.get(adcode=code.SYS_DISTRICT, is_district=1).id
                self.table.filter(id=update_dict.get("id")).update(**update_dict)
                return {"code": code.STATUSCODE_SUCCESS, "msg": "修改成功"}
            else:
                return {"code": code.STATUSCODE_UNSUCCESS, "msg": "该频点在该区域内重复"}
        else:
            return {"code": code.STATUSCODE_UNSUCCESS, "msg": "没有关键信息"}

    def select_info(self, select_dict):
        """
        根据条件检索品殿分类
        :param select_dict:
        :return:
        """
        query = self.table.filter(**select_dict).values().exclude(
            freq=f.UNKNOW_WHITELIST)
        content = list(map(self.formatter_foreign_content, list(query)))
        content = self.formatter_content(content)
        return content

    def get_info_by_district(self, district):
        """
        根据地区获取白名单,一级与二级
        :param district:
        :return:
        """
        # ****************
        sys_dis_id = self.dis.get(adcode=code.SYS_DISTRICT, is_district=1).id
        # -------------- 查询集 ------------------
        query = self.table.all().values("name", "freq", "type", "district")
        # --------------- 结果 --------------------
        # ********** 普通频点 ************
        normal_content = list(query.filter(district=sys_dis_id))
        # *********** 区域频点 ************
        sub_content = list(query.filter(district=district))
        # ************ 台站频点 ***********
        tg_content = list()
        tg_id_list = self.dis.filter(superior=district, is_district=0)
        for tg in tg_id_list:
            tg_id = tg.id
            tg_content.extend(list(query.filter(district=tg_id)))
        # ************ 汇总 ************
        content = normal_content + sub_content + tg_content
        return content

    def get_info_for_mobile(self, mobile):
        """
        根据系统id获取白名单，手机用
        :param mobile:
        :return:
        """
        # ------------- 区域id ----------------------
        # ********** 系统区域id ********************
        sys_dis_id = self.dis.get(adcode=code.SYS_DISTRICT, is_district=1).id
        # ********** 手机所在台站id *****************
        tg_dis_id = self.mob.get(mobile=mobile).district
        # ********** 手机所在区域id *****************
        dis_id = self.dis.get(id=tg_dis_id).superior
        # ------------------ 查询集 ------------------
        _query = self.table.all().values()
        # -------------------- 白名单 ------------------------
        # ********** 通用白名单 ************
        nomal_content = list(_query.filter(district=sys_dis_id))
        # ********** 区域白名单 *************
        district_content = list(_query.filter(district=dis_id))
        # ********** 台站白名单 **************
        tg_content = list(_query.filter(district=tg_dis_id))
        # ********** 汇总 *************
        content = nomal_content + district_content + tg_content
        # ********** 结果处理 ************
        content = self.formatter_content(content)
        # *********** 返回 ******************
        return content

    def get_disid_by_mobile(self, mobile):
        """
        根据手机号获取区域id
        :param mobile:
        :return:
        """
        tg_dis = self.mob.get(mobile=mobile).district
        dis_id = self.dis.get(id=tg_dis).superior
        return dis_id

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

    def get_query_by_district(self, district):
        """
        通过地区获取查询集，包括普通，区域，台站
        :param district:
        :return:
        """
        # 普通频点查询集
        normal_query = self.table.filter(type=1)
        # 区域频点查询集
        distict_query = self.table.filter(district=district)
        # 台站频点查询集
        tg_list = self.dis.filter(superior=district, is_district=0)
        for tg_obj in tg_list:
            tg_query = self.table.filter(district=tg_obj.id)
            distict_query = distict_query | tg_query
        # 合并
        query = normal_query | distict_query
        return query

    def get_query_by_district_nonormal(self, district):
        """
        按区域获取查询集，去掉普通频点
        :param district:
        :return:
        """
        query = self.table.filter(district=district).exclude(type=1)
        return query

    def formatter_foreign_content(self, content):
        """
        外键关联查询
        :param content:
        :return:
        """
        keys = content.keys()
        if "district" in keys:
            try:
                content["district_num"] = content.get("district")
                content["district"] = self.dis.get(id=content.get("district")).name
            except self.dis.model.DoesNotExist:
                content["district_num"] = f.UNKNOW_DISTRICT
                content["district"] = self.dis.get(adcode=f.UNKNOW_DISTRICT).name
        if "type" in keys:
            content["type_num"] = content.get("type")
            try:
                content["type"] = self.whc.table.get(id=content.get("type")).name
            except self.whc.table.model.DoesNotExist:
                content["type_num"] = f.UNKNOW_WHITECATEGORY
                content["type"] = self.whc.table.get(id=f.UNKNOW_WHITECATEGORY).name
        return content

    def make_freq(self):
        """
        修正频点
        :return:
        """
        query = self.table.all()
        ff = freq_formatter()
        for info in query:
            info.freq = ff.mobile_to_django(info.freq)
            info.save()

    def make_whcategory_normal(self):
        """
        修正频点类型
        :return:
        """
        dis_id = self.dis.get(adcode=code.SYS_DISTRICT, is_district=1).id
        query = self.table.filter(district=dis_id)
        wh_type = 1
        for obj in query:
            obj.type = wh_type
            obj.save()
        return code.con

    def make_whcategory(self, s, e):
        """
        修正频点类型，将原类型s修正为e
        :param s:
        :param e:
        :return:
        """
        query = self.table.all()
        for obj in query:
            if obj.type == int(s):
                obj.type = int(e)
                obj.save()

    def make_whcategory_unknow(self):
        """
        将白名单中类型为未知频点改为黑名单
        :return:
        """
        query = self.table.filter(type=4)
        for obj in query:
            print(obj.freq, obj.type)
            if obj.freq == 0:
                print("continue:", obj.freq)
                continue
            obj.type = 5
            obj.save()

    def make_repeat_freq(self):
        """
        修正频点重复问题
        规则：
        １．普通频点在数据库中唯一
        ２．同区域内不可出现重复
        ３．不同区域可重复
        :return:
        """
        # 修正频点所属地区
        self.make_freq_district()
        # 修正普通频点的重复
        normal_wh = self.get_normal_wh()
        # 区域与普通频点重复
        query = self.table.all().exclude(type=1)
        for obj in query:
            if str(obj.freq) in normal_wh:
                print(obj.freq)
                obj.delete()
        # 修正同区域内频点重复
        sys_dis = self.dis.get(adcode=code.SYS_DISTRICT, is_district=1).id
        dis_list = list(map(lambda district: district.get("id"),
                            list(self.dis.filter(superior=sys_dis, is_district=1).values("id"))))
        for dis_id in dis_list:
            query = self.get_query_by_district_nonormal(dis_id)
            # 白名单频点非重复列表
            wh_dis_list = list(set(list(map(lambda wh_freq: wh_freq.get("freq"), list(query.values("freq"))))))
            for wh_freq in wh_dis_list:
                curr_query = query.filter(freq=wh_freq)
                for i in range(curr_query.count() - 1):
                    if i > 0:
                        curr_query[i].delete()

    def make_freq_district(self):
        """
        修正频点所属地区，普通频点属于一级，台站频点所属二级
        :return:
        """
        # 一级行政区id
        sys_dis = self.dis.get(adcode=code.SYS_DISTRICT, is_district=1).id
        query = self.table.all()
        for obj in query:
            # 普通频点都属于一级行政区
            if obj.type == 1:
                obj.district = sys_dis
            else:
                curr_dis = self.dis.get(id=obj.district)
                # 台站所属改为二级行政区所属
                if curr_dis.is_district == 0:
                    obj.district = curr_dis.superior
            obj.save()

    def is_freqLegal_in_dis(self, freq, district):
        """
        判断一个频点在某个地区内是否合法,考虑三级地区
        :param freq:
        :param district:
        :return:
        """
        # 二级行政区表
        sys_dis = self.dis.get(adcode=code.SYS_DISTRICT, is_district=1).id
        sub_dis_list = list(map(lambda info: info.get("id"),
                                list(self.dis.filter(superior=sys_dis, is_district=1).values("id"))))
        sub_dis_list.append(sys_dis)
        # 是否为二级行政区 不是则改为所属二级区域
        if district not in sub_dis_list:
            sub_sub_dis = self.dis.get(id=district)
            district = sub_sub_dis.superior
        query = self.table.all()
        # 是否为普通频点
        normal_list = self.get_normal_wh()
        if str(freq) in normal_list:
            return True
        try:
            obj_type = query.get(freq=freq, district=district).type
            islegal = self.whc.is_type_legal(obj_type)
        except self.table.model.DoesNotExist:
            return False
        else:
            if int(islegal) == 1:
                return True
            else:
                return False


class serWhiteCategory(SerTable):
    def __init__(self):
        SerTable.__init__(self)
        self.table = WhiteListCategory.objects

    def get_info_select(self):
        """
        获取分类列表,(下拉菜单用)
        :return:
        """
        query = self.table.all().values()
        content = list()
        for info in list(query):
            con = dict()
            con["name"] = info.get("name")
            con["num"] = str(info.get("id"))
            content.append(con)
        return content

    def get_info_select_copy(self):
        """
        获取分类列表,(下拉菜单用)
        :return:
        """
        query = self.table.all().values()
        content = list()
        for info in list(query):
            con = dict()
            con["label"] = info.get("name")
            con["value"] = info.get("id")
            content.append(con)
        return content

    def is_type_legal(self, type):
        """
        判断该类型是否合法
        :param type:
        :return:
        """
        try:
            obj_islegal = self.table.get(id=type).islegal
        except self.table.model.DoesNotExist:
            return 0
        else:
            return obj_islegal


class serMobileVersion(SerTable):
    def __init__(self):
        SerTable.__init__(self)
        self.table = MobileVersion.objects


class serRedioTest(SerTable):
    def __init__(self):
        SerTable.__init__(self)
        self.table = RedioTest.objects

    def get_by_mobile(self, mobile):
        """
        通过手机号获取信息
        :param mobile:
        :return:
        """
        mob_id = self.mob.get(mobile=mobile).id
        query = self.table.filter(mobile=mob_id).values().order_by("-time")
        content = self.formatter_content(list(query))
        return content

    def formatter_content(self, content):
        con_list = list()
        for con in content:
            time = con.get("time")
            monitor_id = con.get("monitor")
            info = dict()
            time = time.strftime(code.DATA_FORMATTER)
            monitor = self.mon.get(id=monitor_id).name
            info["time"] = time
            info["monitor"] = monitor
            con_list.append(info)
        return con_list


class serMobileToPlatform(SerTable):
    def __init__(self):
        SerTable.__init__(self)
        self.table = MobileToPlatformInfo.objects


class serPlatform(SerTable):
    def __init__(self):
        SerTable.__init__(self)
        self.table = PlatformInfo.objects
