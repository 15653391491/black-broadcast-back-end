import json
import re
from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator
import traceback
import logging

from big_screen.utils import sys_setting as code
from big_screen.serialization.allSerialization import serMobile, serMonitor, serUserRecord, serMobileNewLocation, \
    serDistrict, serWhiteCategory, serWhiteList, serRedioTest
from big_screen.utils import re_format as f
from big_screen.utils.turn_format import time_formatter
from big_screen.redisOpration.AllOpration import MobListOp

errlog = logging.getLogger("Process")


# Create your views here.


# 表单下拉框信息
class FromSelectView(View):
    # √
    @classmethod
    def get(cls, request):
        """
        表单信息获取
        :param request:
        :return:
        """
        # ---------------- 接收 ------------------
        # ---------------- 验证 ------------------
        # ---------------- 处理 ------------------
        # ******* 序列化器 **********
        dis = serDistrict()
        wc = serWhiteCategory()
        # ******** 组织数据 *********
        all_info = {"name": "全部", "num": "0"}
        content_monitor = list()
        content_mobile = list()
        content_monitor.append(all_info)
        content_mobile.append(all_info)
        # *********** 监测人员 ***************
        query_monitor = dis.mon.filter(is_delete=0).values()
        for info in list(query_monitor):
            con = dict()
            con["name"] = info.get("name")
            con["num"] = str(info.get("id"))
            content_monitor.append(con)
        # *********** 手机 *******************
        query_mobile = dis.mob.filter(is_delete=0).values()
        for info in list(query_mobile):
            con = dict()
            con["name"] = info.get("name")
            con["num"] = str(info.get("id"))
            content_mobile.append(con)
        # ********** 区域 *************
        content_district = dis.get_info_select()
        content_district_bak = dis.get_info_select_bak()
        # ********* 台站 **************
        content_taizhan = dis.get_taizhan_select()
        # ********* 汇总 ***************
        content_freq_category = list()
        content_freq_category_result = wc.get_info_select()
        for fc_info in content_freq_category_result:
            num = fc_info.get("num")
            if str(num) == "4":
                continue
            else:
                content_freq_category.append(fc_info)
        # content_freq_category.append({"name": "全部", "num": "0"})
        info = dict()
        info["district"] = content_district
        info["district_copy"] = content_district_bak
        info["freq_category"] = content_freq_category
        info["mobile"] = content_mobile
        info["monitor"] = content_monitor
        info["taizhan"] = content_taizhan
        # ---------------- 返回 ------------------
        con = code.con
        con["data"] = info
        return JsonResponse(con)


# 移动端名单
class ControlTextView(View):
    # √
    @classmethod
    def get(cls, request):
        """
        获取移动端信息
        :param request:
        :return:
        """
        try:
            # ------------ 接收 -------------
            ret = request.GET.dict()
            select_dict = ret.get("0")
            page = ret.get("page")
            limit = ret.get("limit")
            if page is None:
                page = 1
                limit = 10
            is_select = False
            # ------------ 验证 -------------
            if select_dict is None:
                pass
            else:
                select_dict = json.loads(select_dict)
                is_select = True
            # ------------ 处理 -------------
            # ******** 序列化器 ********
            mob = serMobile()
            mobl = MobListOp()
            mobl.update_mob_list()
            # ******** 查询结果 **********
            if is_select:
                result = mob.select_info(select_dict)
            else:
                result = mob.get_info()
            # ********* 分页 **********
            paginator = Paginator(result, limit)
            content = list()
            for con in paginator.page(page):
                content.append(con)
            # ------------ 返回 -------------
            con = code.con
            con["data"] = content
            con["count"] = len(result)
            return JsonResponse(con)
        except Exception:
            e = traceback.format_exc()
            errlog.warning(e)

    # √
    @classmethod
    def post(cls, request):
        """
        添加移动端
        :param request:
        :return:
        """
        # -------------- 接收 ----------------
        ret = request.body.decode()
        if ret is "":
            ret = {
                "district": "0",
                "name": "未知",
                "mobile": "0",
                "phonenumber": "0",
                "time": ""
            }
        else:
            ret = eval(ret)
        district = ret.get("district")
        name = ret.get("name")
        mobile = ret.get("mobile")
        phonenumber = ret.get("phonenumber")
        time = ret.get("time")
        # -------------- 验证 ----------------
        time_result = re.fullmatch(f.DATE_FORMATTER_RE, time)
        # -------------- 处理 ----------------
        # ******** 格式转化器 ***********
        tf = time_formatter()
        if time_result is None:
            time = tf.now_time_str
        # ******* 序列化器 **********
        mob = serMobile()
        # ******** 插入设备 ************
        insert_dict = dict()
        insert_dict["district"] = district
        insert_dict["name"] = name
        insert_dict["mobile"] = mobile
        insert_dict["phonenumber"] = phonenumber
        insert_dict["time"] = time
        result = mob.insert_info(**insert_dict)
        # ******* 更新redis中mobile 列表 ***********
        moblist_op = MobListOp()
        moblist_op.update_mob_list()
        # -------------- 返回 ----------------
        con = code.con
        con["data"] = result
        return JsonResponse(con)

    # √
    @classmethod
    def delete(cls, request):
        """
        删除移动端
        :param request:
        :return:
        """
        # ----------- 接收 -----------------
        ret = request.GET.dict()
        del_id = ret.get("id")
        # ----------- 验证 -----------------
        # ----------- 处理 -----------------
        # ******** 序列化器 *********
        mob = serMobile()
        # ******** 组织数据 ********
        delete_dict = dict()
        delete_dict["id"] = del_id
        # ******** 处理 *********
        result = mob.delete_info(delete_dict)
        # ******* 更新redis中mobile 列表 ***********
        moblist_op = MobListOp()
        moblist_op.update_mob_list()
        # ----------- 返回 -----------------
        con = code.con
        con["data"] = result
        return JsonResponse(con)

    # √
    @classmethod
    def patch(cls, request):
        """
        修改设备信息
        :param request:
        :return:
        """
        # -------------- 接收 ----------------
        ret = request.body.decode()
        if ret is "":
            ret = {
                "district": "0",
                "name": "未知",
                "phonenumber": "0",
                "time": ""
            }
        else:
            ret = eval(ret)
        district = ret.get("district")
        name = ret.get("name")
        phonenumber = ret.get("phonenumber")
        time = ret.get("time")
        mob_id = ret.get("id")
        # -------------- 验证 ----------------
        # -------------- 处理 ----------------
        # ************ 序列化器 ***********
        mob = serMobile()
        # ************ 组织数据 ***********
        update_dict = dict()
        update_dict["id"] = mob_id
        update_dict["district"] = district
        update_dict["name"] = name
        update_dict["phonenumber"] = phonenumber
        update_dict["time"] = time
        # ************* 更新数据 ************
        result = mob.update_info(update_dict)
        # -------------- 返回 ----------------
        con = code.con
        con["data"] = result
        return JsonResponse(con)


# 移动端位置
class MobileLocationView(View):

    @classmethod
    def post(cls, request):
        """
        根据发来的表单查询手机的工作路径,参数有开始时间,结束时间和设备id
        :param request:
        :return:
        """
        # ---------------- 接收 --------------
        ret = request.body.decode()
        if ret == "":
            pass
        else:
            ret = eval(ret)
        mobile = ret.get("mobile")
        s_time = ret.get("s_time")
        e_time = ret.get("e_time")
        # ---------------- 验证 --------------
        # ---------------- 处理 --------------
        # ********* 序列化器 **********
        s = serMobileNewLocation()
        # ********* 查询条件 *************
        select_dict = dict()
        select_dict["mobile"] = mobile
        select_dict["s_time"] = s_time
        select_dict["e_time"] = e_time
        # ********** 查询 ***********
        content = s.select_info(select_dict)
        content = list(map(lambda info: info.split(","), content))
        # ******* 去掉错误数据 ***************
        if ['x', 'x'] in content:
            content.remove(['x', 'x'])
        if ['0.0', '0.0'] in content:
            content.remove(['0.0', '0.0'])
        # ---------------- 返回 --------------
        con = code.con
        con["data"] = content
        return JsonResponse(con)


# 频点分类
class FreqCategoryView(View):
    @classmethod
    def get(cls, request):
        """
        获取频点分类
        :param request:
        :return:
        """
        # --------------- 接收 --------------------
        ret = request.GET.dict()
        select_dict = ret.get("msg")
        page = ret.get("page")
        limit = ret.get("limit")
        # --------------- 验证 --------------------
        is_select = False
        if select_dict is None:
            pass
        else:
            select_dict = json.loads(select_dict)
            is_select = True
        # --------------- 处理 --------------------
        # ******* 序列化器 *********
        wh = serWhiteList()
        # ******* 结果查询 ********
        if is_select:
            result = wh.select_info(select_dict)
        else:
            result = wh.get_info()
        # ******* 分页 *********
        paginator = Paginator(result, limit)
        content = list()
        for con in paginator.page(page):
            content.append(con)
        # --------------- 返回 --------------------
        con = code.con
        con["data"] = content
        con["count"] = len(result)
        return JsonResponse(con)

    @classmethod
    def post(cls, request):
        """
        添加频点分类
        :param request:
        :return:
        """
        try:
            # --------------- 接收 --------------------
            ret = request.body.decode()
            if ret == "":
                pass
            else:
                ret = eval(ret)
            district = ret.get("district")
            freq = ret.get("freq")
            time = ret.get("time")
            freq_type = ret.get("type")
            name = ret.get("name")
            # --------------- 验证 --------------------
            # --------------- 处理 --------------------
            # ******* 序列化器 *********
            wh = serWhiteList()
            # ****** 组织数据 *********
            insert_dict = dict()
            insert_dict["district"] = district
            insert_dict["type"] = freq_type
            insert_dict["time"] = time
            insert_dict["freq"] = freq
            insert_dict["name"] = name
            # ****** 操作数据 *********
            result = wh.insert_info(insert_dict)
            # --------------- 返回 --------------------
            con = code.con
            con["data"] = result
            return JsonResponse(con)
        except Exception:
            e = traceback.format_exc()
            errlog.info(e)

    @classmethod
    def patch(cls, request):
        """
        修改频点分类
        :param request:
        :return:
        """
        # --------------- 接收 --------------------
        ret = request.body.decode()
        if ret == "":
            pass
        else:
            ret = eval(ret)
        district = ret.get("district")
        freq_type = ret.get("type")
        name = ret.get("name")
        time = ret.get("time")
        freq_id = ret.get("id")
        # --------------- 验证 --------------------
        # --------------- 处理 --------------------
        # ******* 序列化器 *********
        wh = serWhiteList()
        # ****** 组织数据 *********
        update_dict = dict()
        update_dict["district"] = district
        update_dict["type"] = freq_type
        update_dict["name"] = name
        update_dict["time"] = time
        update_dict["id"] = freq_id
        # ****** 更新数据 *******
        result = wh.update_info(update_dict)
        # --------------- 返回 --------------------
        con = code.con
        con["data"] = result
        return JsonResponse(con)

    @classmethod
    def delete(cls, request):
        """
        删除该频点分类
        :param request:
        :return:
        """
        # ----------- 接收 -----------------
        ret = request.GET.dict()
        del_id = ret.get("id")
        # ----------- 验证 -----------------
        # ----------- 处理 -----------------
        # ******** 序列化器 *********
        mob = serWhiteList()
        # ******** 组织数据 ********
        delete_dict = dict()
        delete_dict["id"] = del_id
        # ******** 处理 *********
        result = mob.delete_info(delete_dict)
        # ----------- 返回 -----------------
        con = code.con
        con["data"] = result
        return JsonResponse(con)


# 监测人员
class MonitorView(View):
    # √
    @classmethod
    def get(cls, request):
        """
        获取检测人员信息
        :param request:
        :return:
        """
        # --------------- 接收 --------------------
        ret = request.GET.dict()
        select_dict = ret.get("msg")
        page = ret.get("page")
        limit = ret.get("limit")
        # --------------- 验证 --------------------
        is_select = False
        if select_dict is None:
            pass
        else:
            select_dict = json.loads(select_dict)
            is_select = True
        # --------------- 处理 --------------------
        # ******* 序列化器 *********
        mon = serMonitor()
        # 查询
        if is_select:
            result = mon.select_info(select_dict)
        else:
            result = mon.get_info()
        # ****** 分页 *******
        paginator = Paginator(result, limit)
        content = list()
        for con in paginator.page(page):
            content.append(con)
        # --------------- 返回 --------------------
        con = code.con
        con["data"] = content
        con["count"] = len(result)
        return JsonResponse(con)

    # √
    @classmethod
    def post(cls, request):
        """
        添加检测人员信息
        :param request:
        :return:
        """
        # --------------- 接收 --------------------
        ret = request.body.decode()
        if ret == "":
            pass
        else:
            ret = eval(ret)
        district = ret.get("district")
        idcard = ret.get("idcard")
        name = ret.get("name")
        # --------------- 验证 --------------------
        # --------------- 处理 --------------------
        ff = time_formatter()
        # ******* 序列化器 *********
        mon = serMonitor()
        # ****** 组织数据 *********
        insert_dict = dict()
        insert_dict["district"] = district
        insert_dict["idcard"] = idcard
        insert_dict["time"] = ff.now_time_str
        insert_dict["name"] = name
        # ****** 操作数据 *********
        result = mon.insert_info(**insert_dict)
        # --------------- 返回 --------------------
        con = code.con
        con["data"] = result
        return JsonResponse(con)

    @classmethod
    def delete(cls, request):
        """
        删除检测人员信息
        :param request:
        :return:
        """
        # ---------- 接收 -----------
        ret = request.GET.dict()
        idcard = ret.get("idcard")
        # ---------- 验证 -----------
        # ******　序列化器 ****
        mon = serMonitor()
        # ---------- 处理 -----------
        #
        try:
            mon_id = mon.table.get(idcard=idcard).id
        except mon.table.model.DoesNotExist:
            result = {"code": code.STATUSCODE_UNSUCCESS, "msg": "无该设备"}
        else:
            #
            delete_dict = dict()
            delete_dict["id"] = mon_id
            #
            result = mon.delete_info(delete_dict)
        # ---------- 返回 -----------
        con = code.con
        con["data"] = result
        return JsonResponse(con)

    # √
    @classmethod
    def patch(cls, request):
        """
        修改检测人员信息
        :param request:
        :return:
        """
        # -----------------　接收 ------------------
        ret = request.body.decode()
        ret = eval(ret)
        district = ret.get("district")
        time = ret.get("time")
        name = ret.get("name")
        mon_id = ret.get("id")
        # -----------------　验证 ------------------
        # -----------------　处理 ------------------
        mon = serMonitor()
        update_dict = dict()
        update_dict["name"] = name
        update_dict["time"] = time
        update_dict["district"] = district
        update_dict["id"] = mon_id
        result = mon.update_info(update_dict)
        # -----------------　返回 ------------------
        con = code.con
        con["data"] = result
        return JsonResponse(con)


# 使用记录
class UseRecord(View):
    # √
    @classmethod
    def get(cls, request):
        """
        查询手机使用记录
        """
        # -------------- 接收 ------------------
        ret = request.GET.dict()
        page = ret.get("page")
        limit = ret.get("limit")
        select_dict = ret.get("msg")
        # -------------- 验证 ------------------
        is_select = False
        if select_dict is None:
            pass
        else:
            select_dict = json.loads(select_dict)
            is_select = True
        # -------------- 处理 ------------------
        ur = serUserRecord()
        if is_select:
            result = ur.select_info(select_dict)
        else:
            result = ur.get_info()
        # ********* 分页************
        paginator = Paginator(result, limit)
        content = list()
        for con in paginator.page(page):
            content.append(con)
        # -------------- 返回 ------------------
        con = code.con
        con["data"] = content
        con["count"] = len(result)
        return JsonResponse(con)


class RedioTestView(View):
    def get(self, request):
        """

        :param request:
        :return:
        """
        # ----------- 接收 ---------------
        ret = request.GET.dict()
        mobile = ret.get("mobile")
        # ----------- 验证 ---------------
        # ----------- 处理 ---------------
        rt = serRedioTest()
        result = rt.get_by_mobile(mobile)
        # ----------- 返回 ---------------
        con = code.con
        con["data"] = result
        return JsonResponse(con)
