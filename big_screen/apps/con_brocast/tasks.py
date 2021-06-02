#!/usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import
import logging
import json
import datetime

from big_screen.celery import app
from big_screen.utils import sys_setting as code
from big_screen.redisOpration.AllOpration import massmarkOp, broadcastOp
from con_brocast.Serialization import serBlackRecord
from con_control.Serialization import serDistrict
from con_control.models import District
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
    # *********** 序列化器 ***********
    bro = serBlackRecord()
    dis = serDistrict()
    # *********** 处理 **************
    for con in message:
        adcode = con.pop("adcode")
        try:
            con["district"] = dis.table.get(adcode=adcode, is_district=1).id
        except District.DoesNotExist:
            con["district"] = dis.table.get(adcode=code.SYS_DISTRICT, is_district=1).id
        except Exception:
            con["district"] = dis.table.get(adcode=code.SYS_DISTRICT, is_district=1).id
        bro.insert_info(**con)


@app.task
def expire_broadcast():
    """
    清空过期内容
    １．海量点
    ２．热力图
    ３．轮播表
    :return:
    """
    # --------------- 创建redis操作对象 -----------
    mass = massmarkOp()
    bro = broadcastOp()
    # --------------- 获取数据 --------------------
    # ************* 海量点 **************
    mass_keys = mass.get_keys()
    for key in mass_keys:
        mass_length = mass.list_get_len(key)
        for i in range(mass_length):
            flag = pop_list(mass, key)
            if flag is 2:
                break
    # ************* 热力图 **************
    heat_length = bro.list_get_len("heatmap_n")
    for i in range(heat_length):
        flag = pop_list(bro, "heatmap_n")
        if flag is 2:
            break
    # ************* 轮播表 **************
    scroll_length = bro.list_get_len("scroll_n")
    for i in range(scroll_length):
        flag = pop_list(bro, "scroll_n")
        if flag is 2:
            break


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
    content = list(map(lambda info: json.loads(info), content))[0]
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
