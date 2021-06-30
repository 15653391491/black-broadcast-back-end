#!/usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import

import datetime
import logging

from big_screen.celery import app
from big_screen.redisOpration.AllOpration import isworkingOp, massmarkOp, broadcastOp
# from con_control.Serialization import serMobileNewLocation
from big_screen.serialization.allSerialization import serBlackRecord, serDistrict, serMobileNewLocation
from big_screen.utils import sys_setting as code
from big_screen.utils import tools as t

errlog = logging.getLogger("Process")
Brlog = logging.getLogger("Broadcasting")


@app.task
def save_to_mysql(message):
    """
    黑广播消息队列
    :param message:
    :return:
    """
    Brlog.info("save-to-sql " + message)
    # *********** 序列化器 ***********
    bro = serBlackRecord()
    dis = serDistrict()
    # *********** 处理 **************
    for con in message:
        adcode = con.pop("adcode")
        try:
            con["district"] = dis.table.get(adcode=adcode, is_district=1).id
        except dis.table.model.DoesNotExist:
            con["district"] = dis.table.get(adcode=code.SYS_DISTRICT, is_district=1).id
        except Exception:
            con["district"] = dis.table.get(adcode=code.SYS_DISTRICT, is_district=1).id
        try:
            bro.insert_info(**con)
        except Exception as e:
            errlog.warning(e)


@app.task
def pop_heartbeat():
    """
    清理过期的心跳包,
    １．定时任务逐条访问2号redis仓库
    ２．从右向左遍历每一条队列
    ３．获取每一条信息中的时间与当前时间做对比，时间差超出设置时间范围，或信息中时间大于当前时间则pop，遍历下一条
    ４．时间差小于时间范围则停止遍历
    :return:
    """
    iw = isworkingOp()
    keys = iw.get_keys()
    for key in keys:
        pop_heartbeat_tool(key)


@app.task
def expire_broadcast():
    """
    清空过期内容
    １．海量点
    ２．热力图
    ３．轮播表
    :return:
    """
    pass
    # --------------- 创建redis操作对象 -----------
    # mass = massmarkOp()
    # # --------------- 获取数据 --------------------
    # # ************* 海量点 **************
    # mass_keys = mass.get_keys()
    # for key in mass_keys:
    #     pop_massmark_tool(key)
    # # ************* 热力图 **************
    # pop_heatmap_tool("heatmap_n")
    # # ************* 轮播表 **************
    # pop_scroll_tool("scroll_n")


@app.task
def selectIndexBlackBroadInfo():
    """
    定时查询大屏中的黑广播信息
    :return:
    """
    # ------------ redis ---------------
    bro = broadcastOp()
    mass = massmarkOp()
    # ------------ mysql ---------------
    br = serBlackRecord()
    # ------------ 时间范围 ---------------
    s = t.setting()  # 配置文件
    timeRange = s.get_timeRange()  # 时间范围 分钟
    end = datetime.datetime.now()  # 结束时间
    start = end - datetime.timedelta(minutes=timeRange)  # 开始时间
    # ----------- 查询 ----------------
    select_dict = {
        "time__gte": start,
        "time__lte": end,
        "islegal": 0
    }
    q = br.select(select_dict=select_dict)  # 查询集
    scrollData = br.organizeScroll(q)  # 轮播表数据
    massmarkData = br.organizeMassMark(q)  # 海量点数据
    heatmapData = br.organizeHeatMap(q)  # 热力图数据
    # ------------ 重置缓存 ---------------
    bro.resetScrollData(scrollData)
    bro.resetHeatMapData(heatmapData)
    mass.resetMassMarkData(massmarkData)
    return scrollData


def pop_list(con, key):
    """
    清理用工具
    :param con:
    :param key:
    :return:
    """
    s = t.setting()
    now = datetime.datetime.now()
    content = con.list_get_tail(key)
    if len(content) is 0:
        return 0
    if type(content) is dict:
        time = datetime.datetime.strptime(content.get("time"), code.DATA_FORMATTER)
    elif type(content) is list:
        time = datetime.datetime.strptime(content[0], code.DATA_FORMATTER)
    else:
        return 0
    timediff = now - time
    if timediff.seconds > s.get_timeRange():
        con.list_pop(key)
        return 1
    else:
        return 2


def pop_heartbeat_tool(key):
    """
    心跳包过期工具,针对某一条队列
    1.从右向左遍历该队列
    2.逐条对比心跳包时间Th与当前时间Tn
    3.Th>Tn是为错误时间,直接pop
    4.时间差大于2m时: 1.获取存储的该手机最新新心跳包时间对比时间差 大于5m则存储,2.pop
    :param key:
    :return:
    """
    # --------- 准备 ---------------
    iw = isworkingOp()  # redis操作类
    now = datetime.datetime.now()  # 当前时间
    # --------- 处理 ---------------
    list_len = iw.list_len(key)
    for i in range(list_len):  # 从右往左遍历
        heartbeatinfo = iw.list_get_head(key)
        info_time = heartbeatinfo.get("time")
        info_time = list(map(lambda this_time: datetime.datetime.strptime(this_time, code.DATA_FORMATTER),
                             [info_time]))[0]  # 心跳包中的时间
        if info_time > now:  # 心跳包中的时间晚于当前时间为错误情况
            iw.list_pop(key)
        timediff = now - info_time  # 时间差
        if timediff.total_seconds() > code.EXPIRATION_TIME:
            iw.list_pop(key)  # pop队列
            ml = serMobileNewLocation()  # 心跳包保存序列化器
            # ------------------------ 组织心跳包数据 --------------------------
            heartbeatinfo.pop("address")
            try:
                insert_dict = ml.formatter_foreign_content(heartbeatinfo)
            except ml.mob.model.DoesNotExist:
                continue
            else:
                lnglat = insert_dict.get("lnglat")
                if lnglat == "x,x":
                    continue
                if lnglat == "x-x":
                    continue
            # -----------------------------------------------------------
            mysql_time = ml.get_recent_time(key)  # 数据库中该手机存储的最新时间
            if mysql_time == 0:
                ml.insert_info(**insert_dict)
            timediff2 = info_time - mysql_time  # 时间差
            if timediff2.total_seconds() > code.RECORD_EXPIRATION_TIME:
                ml.insert_info(**insert_dict)


def pop_massmark_tool(key):
    """
    定时清理黑广播列表
    1.针对一条队列
    2.从右向左遍历，
    3.取当前时间与信息中的时间做差，若当期时间小于信息时间则pop
    4.差值与配置文件中的时间范围做比较，大于时间范围则pop，小于时间范围则停止遍历
    :param key:
    :return:
    """
    # --------- 准备 ---------------
    mass = massmarkOp()  # redis操作类
    now = datetime.datetime.now()  # 当前时间
    s = t.setting()  # 配置文件
    timerange = s.get_timeRange()
    # --------- 处理 ---------------
    list_len = mass.list_len(key)
    for i in range(list_len):  # 从右往左遍历
        massmarkInfo = mass.list_get_head(key)
        info_time = massmarkInfo.get("time")
        info_time = list(map(lambda this_time: datetime.datetime.strptime(this_time, code.DATA_FORMATTER),
                             [info_time]))[0]  # 心跳包中的时间
        if info_time > now:  # 心跳包中的时间晚于当前时间为错误情况
            mass.list_pop(key)
        timediff = now - info_time  # 时间差
        if timediff.total_seconds() > timerange:
            mass.list_pop(key)  # pop队列
        else:
            continue


def pop_heatmap_tool(key):
    """

    :param key:
    :return:
    """
    # --------- 准备 ---------------
    bro = broadcastOp()
    now = datetime.datetime.now()  # 当前时间
    s = t.setting()  # 配置文件
    timerange = s.get_timeRange()
    # --------- 处理 ---------------
    list_len = bro.list_len(key)
    for i in range(list_len):  # 从右往左遍历
        massmarkInfo = bro.list_get_head(key)
        info_time = massmarkInfo.get("time")
        info_time = list(map(lambda this_time: datetime.datetime.strptime(this_time, code.DATA_FORMATTER),
                             [info_time]))[0]  # 心跳包中的时间
        if info_time > now:  # 心跳包中的时间晚于当前时间为错误情况
            bro.list_pop(key)
        timediff = now - info_time  # 时间差
        if timediff.total_seconds() > timerange:
            bro.list_pop(key)  # pop队列
        else:
            continue


def pop_scroll_tool(key):
    """

    :return:
    """
    # --------- 准备 ---------------
    bro = broadcastOp()
    now = datetime.datetime.now()  # 当前时间
    s = t.setting()  # 配置文件
    timerange = s.get_timeRange()
    # --------- 处理 ---------------
    list_len = bro.list_len(key)
    for i in range(list_len):  # 从右往左遍历
        massmarkInfo = bro.list_get_head(key)
        info_time = massmarkInfo[0]
        info_time = list(map(lambda this_time: datetime.datetime.strptime(this_time, code.DATA_FORMATTER),
                             [info_time]))[0]  # 心跳包中的时间
        if info_time > now:  # 心跳包中的时间晚于当前时间为错误情况
            bro.list_pop(key)
        timediff = now - info_time  # 时间差
        if timediff.total_seconds() > timerange:
            bro.list_pop(key)  # pop队列
        else:
            continue


def makeScrollData(info):
    time = info.get("time")
    time = time.strftime(code.DATA_FORMATTER)
    freq = info.get("freq")
    category = info.get("category__name")
    address = info.get("address")
    return [time, freq, category, address]
