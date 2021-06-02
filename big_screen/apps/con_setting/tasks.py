#!/usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import
import datetime
import json

from big_screen.celery import app
from big_screen.redisOpration.AllOpration import isworkingOp
from big_screen.utils import sys_setting as code
from con_control.Serialization import serMobileNewLocation


@app.task
def pop_heartbeat():
    """
    清理过期的心跳包
    :return:
    """
    # 获取当前时间
    now = datetime.datetime.now()
    iw = isworkingOp()
    keys = iw.get_keys()
    from con_control.models import MobileInfo
    for key in keys:
        heartbeat = list(map(lambda heartbeat_: json.loads(heartbeat_), iw.list_get_tail(key)))[0]
        heartbeat.pop("address")
        time = \
            list(map(lambda this_time: datetime.datetime.strptime(this_time, code.DATA_FORMATTER),
                     [heartbeat.get("time")]))[
                0]
        timerify = now - time
        if timerify.seconds > code.EXPIRATION_TIME:
            s = serMobileNewLocation()
            try:
                insert_dict = s.formatter_foreign_content(heartbeat)
            except MobileInfo.DoesNotExist:
                continue
            else:
                lnglat=insert_dict.get("lnglat")
                if lnglat is "x,x":
                    continue
                else:
                    s.insert_info(**insert_dict)
            iw.list_pop(key)
        else:
            continue
