# Create your views here.
from django.views import View
from django.http import JsonResponse
import traceback
import logging

from big_screen.utils import sys_setting as code
from big_screen.utils import tools as t
from big_screen.redisOpration.AllOpration import broadcastOp
from .tasks import get_chart_data, get_category_data, get_heatmap_data
from big_screen.serialization.allSerialization import serBlackRecord, serBlackCategory

errlog = logging.getLogger("Process")


class ChartInfoView(View):
    @classmethod
    def get(cls, request):
        """
        获取图表数据
        :param request:
        :return:
        """
        try:
            # --------- 接收 -----------
            # --------- 验证 -----------
            # --------- 处理 -----------
            # ********* 系统开始时间 **********
            s = t.setting()
            start_day = s.start_time
            # ********* 图表数据 *************
            br_con = broadcastOp()
            chart_data = br_con.kv_get("chart_data")
            # --------- 返回 -----------
            info = dict()
            info["start_day"] = start_day
            info["chart_data"] = chart_data
            con = code.con
            con["data"] = info
            return JsonResponse(con)
        except Exception:
            e = traceback.format_exc()
            errlog.warning(e)

    @classmethod
    def post(cls, request):
        """
        根据时间返回图表数据
        :param request:
        :return:
        """
        # ----------- 接收 -------------------
        ret = request.body.decode()
        ret = eval(ret)
        s_time = ret.get("s_time")
        e_time = ret.get("e_time")
        # ----------- 验证 -------------------
        # ----------- 处理 -------------------
        br = serBlackRecord()  # 序列化器
        bc = serBlackCategory()
        select_dict = dict()
        select_dict["s_time"] = s_time
        select_dict["e_time"] = e_time
        result_obj = br.select_obj(select_dict)

        # # *************** 种类统计 **************
        category_info = list()
        category_type = bc.get_id_list()
        for c_type in category_type:
            info = dict()
            info["name"] = c_type.get("name")
            info["value"] = result_obj.filter(category=c_type.get("id")).count()
            category_info.append(info)
        # ----------- 返回 -------------------
        con = code.con
        con["data"] = category_info
        return JsonResponse(con)


class HeatMapView(View):
    @classmethod
    def get(cls, request):
        """
        热力图数据
        :param request:
        :return:
        """
        # --------------- 接收 --------------------
        ret = request.GET
        # --------------- 验证 --------------------
        # --------------- 处理 --------------------
        # ******* redis操作类 **********
        bro = broadcastOp()
        # ******* 热力图数据 ***********
        heatmap_data = bro.kv_get("heatmap_c")
        # --------------- 返回 --------------------
        con = code.con
        con["data"] = heatmap_data
        return JsonResponse(con)

    @classmethod
    def post(cls, request):
        """
        根据时间返回图表数据
        :param request:
        :return:
        """
        # ----------- 接收 -------------------
        ret = request.body.decode()
        print(ret)
        ret = eval(ret)
        s_time = ret.get("s_time")
        e_time = ret.get("e_time")
        # ----------- 验证 -------------------
        # ----------- 处理 -------------------
        br = serBlackRecord()  # 序列化器
        select_dict = dict()  # 检索条件
        select_dict["s_time"] = s_time
        select_dict["e_time"] = e_time
        result_obj = br.select_obj(select_dict)  # 查询集
        contant = list()  # 结果
        for obj in list(result_obj.values("lnglat")):
            lnglat = obj.get("lnglat").split(",")
            info = dict()
            info["lng"] = lnglat[0]
            info["lat"] = lnglat[1]
            info["count"] = 1
            contant.append(info)
        # ----------- 返回 -------------------
        con = code.con
        con["data"] = contant
        return JsonResponse(con)


class FlushDataView(View):
    @classmethod
    def get(cls, request):
        """
        刷新数据,根据请求路径中的参数判断是那些数据，刷新redis返回并新数据
        :param request:
        :return:
        """
        # --------------- 接收 -------------
        ret = request.GET.dict()
        flush_type = ret.get("type")
        # --------------- 验证 -------------
        # --------------- 处理 -------------
        con = code.con
        if flush_type == "chart":
            info = get_chart_data()
            con["data"] = info
            return JsonResponse(con)
        if flush_type == "heatmap":
            info = get_heatmap_data()
            con["data"] = info
            return JsonResponse(con)
        if flush_type == "category":
            info = get_category_data()
            con["data"] = info
            return JsonResponse(con)
        # --------------- 返回 -------------
        con = code.con_false
        return JsonResponse(con)
