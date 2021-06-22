from django.views import View
from django.http import JsonResponse
import logging
import traceback

from big_screen.utils import sys_setting as code
from big_screen.redisOpration.AllOpration import isworkingOp
from big_screen.utils import tools as t

Helog = logging.getLogger("Heartbeat")
errlog = logging.getLogger("Process")
lnlog = logging.getLogger("Lnglat")


# Create your views here.
# √
class IsWrokon(View):
    @classmethod
    def post(cls, request):
        """
        心跳包存储
        :param request:
        :return:
        """
        # ---------------------- 接收数据 ----------------------
        ret = eval(request.body.decode())
        # ----------------------- 心跳包redis仓库操作类 --------------------
        iw = isworkingOp()
        # ---------------------- 存入redis ---------------------------
        k, v = iw.formatter_info(ret)
        iw.list_push(k, v)
        # --------------------- 返回 ---------------------------------
        return JsonResponse(code.con)


class SetInfoView(View):
    def get(self, request):
        """
        获取配置信息
        :param request:
        :return:
        """
        # ------------- 接收 -------------------
        # ------------- 验证 -------------------
        # ------------- 处理 -------------------
        # ********** 配置信息操作类 **************
        s = t.setting()
        # ********** 配置信息 ****************
        timerange = s.timerange
        chart_cycle = s.chart_selectcycle
        massmark_cycle = s.massmark_selectcycle
        isworking_cycle = s.isworking_selectcycle
        # ********* 组织数据 ************
        info_dict = dict()
        info_dict["timerange"] = timerange
        info_dict["chart"] = chart_cycle
        info_dict["massmark"] = massmark_cycle
        info_dict["isworking"] = isworking_cycle
        # ------------- 返回 -------------------
        con = code.con
        con["data"] = info_dict
        return JsonResponse(con)

    def post(self, request):
        """
        修改配置信息
        :param request:
        :return:
        """
        try:
            # ---------- 接收 --------------
            ret = request.body.decode()
            ret = eval(ret)
            keys = ret.keys()
            # ********** 配置文件操作　**********
            s = t.setting()
            if "timeRange" in keys:  # 黑广播展示时间范围
                timeRange = ret.get("timeRange")
                s.save_timeRange(timeRange)
                con = code.con
                return JsonResponse(con)
            if "broad" in keys:  # 黑广播更新周期
                br_cycle = ret.get("broad")
                s.set("broad", br_cycle)
                con = code.con
                return JsonResponse(con)
            if "chart" in keys:
                chart_cycle = ret.get("chart")
                s.set("chart", chart_cycle)
                con = code.con
                return JsonResponse(con)
            if "isworking" in keys:
                iw_cycle = ret.get("isworking")
                s.set("isworking", iw_cycle)
                con = code.con
                return JsonResponse(con)
        except Exception:
            traceback.print_exc()
