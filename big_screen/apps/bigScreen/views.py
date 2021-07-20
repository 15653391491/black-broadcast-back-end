import json
import copy
import logging
from django.http import JsonResponse
from dwebsocket.decorators import accept_websocket
from django_redis import get_redis_connection
import traceback

from big_screen.utils import sys_setting as code
from big_screen.redisOpration.AllOpration import isworkingOp, massmarkOp, broadcastOp
from big_screen.serialization.allSerialization import serMobile

socket_obj = list()
errlog = logging.getLogger("Process")


# Create your views here.
# -------------------------- socket接口 ---------------------------
# √
# @login_required
@accept_websocket
def websocketmassmark(request):
    """
    首页海量点websocket,加轮播表
    :param request:
    :return:
    """
    try:
        # --------------- 返回 -----------------------
        if request.is_websocket():
            while True:
                content = select_broadcast_data()
                request.websocket.send(json.dumps(content))
                request.websocket.wait()
        else:
            content = select_broadcast_data()
            con = code.con
            con["data"] = content
            return JsonResponse(con)
    except Exception:
        e = traceback.format_exc()
        errlog.warning(e)


# √
# @login_required
@accept_websocket
def websocketchart(request):
    """
    首页图表websocket
    :param request:
    :return:
    """
    try:
        if request.is_websocket():
            while True:
                chart_con = get_redis_connection('chart')
                counter = chart_con.get('counter').decode()
                chart_year_month = chart_con.get('chart_year_month').decode()
                category = chart_con.get('category').decode()
                time_count = chart_con.get('time_count').decode()
                try:
                    mobileSummary = chart_con.get("mobileSummary").decode()
                    regionSummary = chart_con.get("regionSummary").decode()
                except Exception:
                    mobileSummary = []
                    regionSummary = []
                else:
                    mobileSummary = json.loads(mobileSummary)
                    regionSummary = json.loads(regionSummary)
                data = {
                    'counter': json.loads(counter),
                    'chart_year_month': json.loads(chart_year_month),
                    'category': json.loads(category),
                    'time_count': json.loads(time_count),
                    "mobileSummary": mobileSummary,
                    "regionSummary": regionSummary
                }
                # ---------------------------------------- 发送数据 ---------------------------------------
                request.websocket.send(json.dumps(data))
                request.websocket.wait()
        else:
            chart_con = get_redis_connection('chart')
            counter = chart_con.get('counter').decode()
            chart_year_month = chart_con.get('chart_year_month').decode()
            category = chart_con.get('category').decode()
            time_count = chart_con.get('time_count').decode()
            mobileSummary = chart_con.get("mobileSummary").decode()
            regionSummary = chart_con.get("regionSummary").decode()
            data = {
                'counter': json.loads(counter),
                'chart_year_month': json.loads(chart_year_month),
                'category': json.loads(category),
                'time_count': json.loads(time_count),
                "mobileSummary": json.loads(mobileSummary),
                "regionSummary": json.loads(regionSummary)
            }
            return JsonResponse(data)
    except Exception:
        e = traceback.format_exc()
        errlog.warning(e)


# √
@accept_websocket
def websocketisworkon(request):
    """
    查看正在工作的手机，正在工作的设备数量、每个设备的坐标、电话、持有人姓名
    :param request:
    :return:
    """
    try:
        if request.is_websocket():
            while True:
                con = select_isworkon_data()
                request.websocket.send(json.dumps(con))
                request.websocket.wait()
        else:
            con = select_isworkon_data()
            return JsonResponse(con)
    except Exception:
        e = traceback.format_exc()
        errlog.warning(e)


# ------------- 工具 -----------------------
def flushwebsocket(request):
    """
    刷新所有websocket
    :param request:
    :return:
    """
    for obj in socket_obj:
        obj.close()
    return JsonResponse({'code': code.STATUSCODE_SUCCESS, "msg": 'ok'})


def select_broadcast_data():
    """
    获取轮播表、海量点、热力图所需数据
    :return:
    """
    # --------------- 获取数据 --------------------
    mass = massmarkOp()
    bro = broadcastOp()
    # --------------- 组织数据 -------------------
    content = dict()
    # ******** 轮播表 *************
    scroll_content = bro.list_get("scroll_n")
    if scroll_content is 0:
        scroll_content = list()
    else:
        scroll_content = list(map(lambda info: json.loads(info), scroll_content))
    content["scroll"] = scroll_content
    # ******* 热力图 **************
    heatmap_content = bro.list_get("heatmap_n")
    if heatmap_content is 0:
        heatmap_content = list()
    else:
        heatmap_content = list(map(lambda info: json.loads(info), heatmap_content))
    content["heatmap"] = heatmap_content
    # *************** 海量点 ********
    massmark_content = mass.get_for_view()
    content["massmark"] = massmark_content
    return content


def select_isworkon_data():
    # ------------------------- 类准备 -----------------------------
    iw = isworkingOp()
    keys = iw.get_keys()
    s = serMobile()
    # ------------------------- 组织数据 ----------------------------
    info_dict = dict()
    info_dict["count"] = len(keys)
    info_dict["mobile_list"] = list()
    for key in keys:
        info = dict()
        content = iw.list_get_tail(key)
        mobileObjList = map(lambda data_dict: s.table.get(mobile=data_dict["mobile"]), content)
        mobileList = [info for info in mobileObjList]
        mobile = mobileList[0]
        info["lnglat"] = content[0]["lnglat"]
        info["phonenumber"] = mobile.phonenumber
        info["monitor"] = mobile.name
        try:
            info["address"] = content[0]["address"]["formatted_address"]
        except Exception:
            info["address"] = ""
        # info
        info_dict["mobile_list"].append(info)
    # -------------------------- 返回 ------------------------------
    con = code.con
    con["data"] = info_dict
    return con
