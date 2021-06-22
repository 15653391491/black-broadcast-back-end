import json
import logging
import os
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View
from django_redis import get_redis_connection
import datetime
import traceback
from time import clock
import pickle

from big_screen.serialization.allSerialization import serMobile, serBlackRecord, \
    serBlackCategory, serWhiteCategory, serUserRecord
from big_screen.utils import tools as t, sys_setting as code
from big_screen.utils import re_format
from big_screen.redisOpration.AllOpration import ObjectOp

errlog = logging.getLogger('Process')
Brlog = logging.getLogger('Broadcasting')
bodylog = logging.getLogger("body")

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))))


class BroadcastTextView(View):

    @classmethod
    def get(cls, request):
        """
        获取黑广播
        1.根据条件检索黑广播记录:种类category,时间范围 starttime,endtime,设备phone,频点freq
        2.无条件获取白名单之外的黑广播信息
        3.限制数量
        :param request:
        :return:
        """
        start = clock()
        # ------------- 接收 ------------------
        ret = request.GET.dict()
        limit = ret.get("limit")
        page = ret.get("page")
        # ------------- 验证 ------------------
        # ******** 序列化器 **********
        br = serBlackRecord()
        ur = serUserRecord()
        # ********** 是否需要检索 ************
        # -------------- 处理 -----------------
        result = br.get_info()
        # ********* 分页 *************
        paginator = Paginator(result, limit)
        # 缓存
        content = paginator.page(page).object_list
        for info in content:
            mob_id = info.get("mobile__id")
            time = info.get("time")
            record_obj = ur.get_recent_record2(mob_id, time)
            info["monitor"] = record_obj.get("monitor")
            info["freq__num"] = 4
        # -------------- 返回 -----------------
        con = code.con
        con["data"] = content
        con["count"] = paginator.count
        end = clock()
        errlog.info('未经过缓存: %s Seconds' % (end - start))
        return JsonResponse(con)

    @classmethod
    def post(cls, request):
        # ------------- 接收 ------------------
        ret = eval(request.body.decode())
        limit = ret.get("limit")
        page = ret.get("page")
        select_info = ret.get("msg")
        # ------------- 验证 ------------------
        # -------------- 处理 -----------------
        oo = ObjectOp()
        # ******** 序列化器 **********
        br = serBlackRecord()
        ur = serUserRecord()
        result = br.select_info(select_info)
        paginator = Paginator(result, limit)
        content = list()
        for info in paginator.page(page):
            mob_id = info.get("mobile__id")
            time = info.get("time")
            record_obj = ur.get_recent_record2(mob_id, time)
            info["monitor"] = record_obj.get("monitor")
            info["freq__num"] = 4
            content.append(info)
        # -------------- 返回 -----------------
        con = code.con
        con["data"] = content
        con["count"] = paginator.count
        return JsonResponse(con)

    @classmethod
    def patch(cls, request):
        """
        修改黑广播
        １．修改黑广播的联系方式和备注
        :param request:
        :return:
        """
        # ----------- 接收 --------------
        ret = request.body.decode()
        ret = eval(ret)
        category = ret.get("category")
        address = ret.get("address")
        contact = ret.get("contact")
        common = ret.get("common")
        br_type = ret.get("type")
        br_id = ret.get("id")
        # ----------- 验证 --------------
        # ********* 序列化器 **********
        br = serBlackRecord()
        wc = serWhiteCategory()
        # ------------ 处理 -------------
        # ******* 判断修改后类型是否合法 *************
        islegal = wc.is_type_legal(br_type)
        # ****** 组织数据 *******
        update_dict = dict()
        update_dict["category"] = category
        update_dict["address"] = address
        update_dict["contact"] = contact
        update_dict["common"] = common
        update_dict["islegal"] = islegal
        update_dict["id"] = br_id
        # ******** 更新数据库 ************
        result = br.update_info(update_dict)
        # ------------ 返回 -------------
        con = code.con
        con["data"] = result
        return JsonResponse(con)


class GetInfoView(View):
    @classmethod
    def get(cls, request):
        """
        检索表单所用信息
        获取一些基本信息 种类、所属地区等
        :param request:
        :return:
        """
        try:
            #  ------------ 接收 -------------------
            # -------------- 验证 ------------------
            # -------------- 处理 ------------------
            # ******* 序列化器 **********
            bc = serBlackCategory()
            mob = serMobile()
            wc = serWhiteCategory()
            # ******* 查询数据 **********
            bc_content = bc.get_info_select()
            mob_content = mob.get_info_select()
            wc_content = wc.get_info_select()
            # ******* 组织数据 ***********
            bc_base_content = [{"name": "全部", "num": "0"}]
            bc_base_content.extend(bc_content)
            mob_base_content = [{"label": "全部", "value": "0"}]
            mob_base_content.extend(mob_content)
            # -------------- 返回 ------------------
            info = dict()
            info["category"] = bc_base_content
            info["mobile"] = mob_base_content
            info["whcategory"] = wc_content
            info["category-change"] = bc_content
            con = code.con
            con["data"] = info
            return JsonResponse(con)
        except Exception:
            traceback.print_exc()


class RegionRetrievalView(View):
    @classmethod
    def get(cls, request):
        """
        根据区域对黑光播进行检索
        :param request:
        :return:
        """
        # ---------------- 接收 -----------------
        ret = request.GET.dict()
        page = ret.get("page")
        limit = ret.get("limit")
        timerange = ret.get("time")
        adcode = ret.get("adcode")
        # ---------------- 验证 -----------------
        # ********* 序列化器 **********
        br = serBlackRecord()
        # ********* 验证 ***********
        try:
            dis_id = br.dis.get(adcode=adcode, is_district=1).id
        except br.dis.model.DoesNotExist:
            dis_id = br.dis.get(adcode=re_format.UNKNOW_ADCODE, is_district=1).id
        # ---------------- 处理 -----------------
        # ******** 检索字典 **********
        select_dict = dict()
        # ********** 时间范围 **********
        if timerange != "-1":
            e_time = datetime.datetime.now()
            time_diff = datetime.timedelta(int(timerange))
            s_time = (e_time - time_diff).date()
            e_time = e_time.strftime(re_format.DATA_FORMATTER)
            s_time = s_time.strftime(re_format.DATA_FORMATTER)
            select_dict["s_time"] = s_time
            select_dict["e_time"] = e_time
        # ************ 区域 *************
        select_dict["district"] = dis_id
        # ******* 一级 ************
        city_result = br.select_info(select_dict)
        # ****** 二级 ************
        sub_dis = br.dis.filter(superior=dis_id, is_district=1)
        sub_result = list()
        if len(sub_dis) is 0:
            pass
        else:
            for sub in sub_dis:
                select_dict["district"] = sub.id
                sub_sub_result = br.select_info(select_dict)
                sub_result.extend(sub_sub_result)
        city_result.extend(sub_result)
        # ************ 分页 **************
        paginator = Paginator(city_result, limit)
        content = list()
        for con in paginator.page(page):
            con["freq__num"] = 4
            content.append(con)
        # ---------------- 返回 -----------------
        con = code.con
        con["data"] = content
        con["count"] = len(city_result)
        return JsonResponse(con)


class ChartView(View):
    # √
    @classmethod
    def get(cls, request):
        """
        图表数据
        :param request:
        :return:
        """
        if request.user.is_authenticated():
            # --------------- 读配置 ---------------------------
            s = t.setting()
            start_day = s.start_time
            # ---------------- 建立redis连接 -------------------
            chart_con = get_redis_connection('broadcast')
            chart_data = chart_con.get('chart_data').decode()
            # ------------------- 组织数据 ---------------------
            con = json.loads(chart_data)
            con['start_day'] = '/'.join(start_day.split('-'))
            return JsonResponse(con)

    # √
    @classmethod
    def post(cls, request):
        """
        时间选择器
        :param request:
        :return:
        """
        # try:
        # if request.user.is_authenticated():
        # ---------------- 接收请求 --------------------------
        ret = eval(request.body.decode())
        # ---------------- 序列化查询数据 --------------------
        s = serBlackRecord()
        content = s.count_by_category(ret)
        #
        con = {
            'category': content
        }
        return JsonResponse(con)


class HeatMapView(View):
    # √
    @classmethod
    def get(cls, request):
        """
        热力图
        :param request:
        :return:
        """
        ret = request.GET
        errlog.info(ret)
        heatmap_con = get_redis_connection('broadcast')
        heatmap_data = heatmap_con.get('heatmap_c').decode()
        con = json.loads(heatmap_data)
        return JsonResponse(con)

    # √
    @classmethod
    def post(cls, request):
        """
        时间选择器
        :param request:
        :return:
        """
        # if request.user.is_authenticated():
        # ------------ 检索请求 ----------------------------------
        ret = eval(request.body.decode())
        select_dict = dict()
        select_dict["s_time"] = t.heat_to_nomal(ret.get("s_time"))
        select_dict["e_time"] = t.heat_to_nomal(ret.get("e_time"))
        # -------------------------- 序列化获取数据 ----------------------
        s = serBlackRecord()
        info_list = s.select_info(select_dict)
        # ------------------------- 组织数据 ----------------------------
        content = list()
        for info in info_list:
            content.append(info.get("lnglat"))
        # ------------------------ 返回数据 -----------------------------
        con = {
            "code": code.STATUSCODE_SUCCESS,
            "msg": "success",
            "ret": content
        }
        return JsonResponse(con)


def selectBroadcastData(request):
    """
    检索黑广播
    :param request:
    :return:
    """
    pass
