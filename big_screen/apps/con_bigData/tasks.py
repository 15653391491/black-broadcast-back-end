import datetime as d

from big_screen.celery import app
from big_screen.utils import tools as t
from big_screen.serialization.allSerialization import serBlackRecord, serBlackCategory
from big_screen.redisOpration.AllOpration import broadcastOp


@app.task
def save_chart_data():
    """
    保存控制中心的图表信息
    :return:
    """
    # -------------- 准备 ---------------
    # ******** 配置文件 **********
    s = t.setting()
    # ********* 序列化器 **********
    bro = serBlackRecord()  # 黑广播
    bc = serBlackCategory()  # 种类
    # ********** redis操作类 *************
    bro_con = broadcastOp()
    # ********* 查询集 *************
    bro_obj = bro.get_info_obj()
    # *********** 时间范围 ***************
    today = d.datetime.now()
    s_time = s.getStartDay_datetime()
    day_range = today - s_time
    # ---------------- 数据组织 -------------------
    # ********* 每日统计 *************
    now = list()
    for i in range(day_range.days + 1):
        obj = s_time + d.timedelta(days=i)
        obj_next = obj + d.timedelta(days=1)
        num = bro_obj.filter(time__gte=obj, time__lt=obj_next).count()
        now.append(num)
    # **************** 年统计 ****************
    year_count = list()
    for i in range(13):
        if i is 0:
            continue
        content = bro_obj.filter(time__month=i).count()
        year_count.append(content)
    # *************** 月统计 ***************
    month_count = list()
    for i in range(32):
        if i is 0:
            continue
        content = bro_obj.filter(time__day=i).count()
        month_count.append(content)
    # *************** 日统计 *************
    day_count = list()
    for i in range(24):
        content = bro_obj.filter(time__hour=i).count()
        day_count.append(content)
    # *************** 种类统计 **************
    category_info = list()
    category_type = bc.get_id_list()
    for c_type in category_type:
        info = dict()
        info["name"] = c_type.get("name")
        info["value"] = bro_obj.filter(category=c_type.get("id")).count()
        category_info.append(info)
    # ************* 数据综合 *************
    con = dict()
    con["data_list"] = now
    con["year_count"] = year_count
    con["month_count"] = month_count
    con["day_count"] = day_count
    con["category"] = category_info
    # ------------------ 保存redis -------------------
    bro_con.kv_set("chart_data", con)


@app.task
def heat_map_data():
    # --------------- 准备 -----------------
    # ********** 当前日期 ***********
    date = d.datetime.now()
    # ********** 序列化器 ***********
    s = serBlackRecord()
    # ********** redis操作类 ********
    bro_con = broadcastOp()
    # ********** 查询集 *************
    bro_obj = list(s.get_info_obj().filter(time__year=date.year, time__month=date.month).values("lnglat"))
    # ---------------- 组织数据 ----------------
    lnglat_list = list()
    for bro in bro_obj:
        lnglat = bro.get("lnglat").split(",")
        info = dict()
        info["lng"] = lnglat[0]
        info["lat"] = lnglat[1]
        info["count"] = 1
        lnglat_list.append(info)
    con = {
        "location_list": lnglat_list
    }
    # ----------------- 保存redis ---------------
    bro_con.kv_set("heatmap_c", con)


def get_chart_data():
    """
    返回图表数据，更新redis
    :return:
    """
    # -------------- 更新redis -----------
    save_chart_data.delay()
    # -------------- 准备 ---------------
    # ******** 配置文件 **********
    s = t.setting()
    # ********* 序列化器 **********
    bro = serBlackRecord()  # 黑广播
    bc = serBlackCategory()  # 种类
    # ********* 查询集 *************
    bro_obj = bro.get_info_obj()
    # *********** 时间范围 ***************
    today = d.datetime.now()
    s_time = s.getStartDay_datetime()
    day_range = today - s_time
    # ---------------- 数据组织 -------------------
    # ********* 每日统计 *************
    now = list()
    for i in range(day_range.days + 1):
        obj = s_time + d.timedelta(days=i)
        obj_next = obj + d.timedelta(days=1)
        num = bro_obj.filter(time__gte=obj, time__lt=obj_next).count()
        now.append(num)
    # **************** 年统计 ****************
    year_count = list()
    for i in range(13):
        if i is 0:
            continue
        content = bro_obj.filter(time__month=i).count()
        year_count.append(content)
    # *************** 月统计 ***************
    month_count = list()
    for i in range(32):
        if i is 0:
            continue
        content = bro_obj.filter(time__day=i).count()
        month_count.append(content)
    # *************** 日统计 *************
    day_count = list()
    for i in range(24):
        content = bro_obj.filter(time__hour=i).count()
        day_count.append(content)
    # ************* 数据综合 *************
    con = dict()
    con["data_list"] = now
    con["year_count"] = year_count
    con["month_count"] = month_count
    con["day_count"] = day_count
    return con


def get_category_data():
    """
    获取种类信息，更新redis
    :return:
    """
    # -------------- 更新redis -----------
    save_chart_data.delay()
    # -------------- 准备 ---------------
    # ********* 序列化器 **********
    bro = serBlackRecord()  # 黑广播
    bc = serBlackCategory()  # 种类
    # ********* 查询集 *************
    bro_obj = bro.get_info_obj()
    # ---------------- 数据组织 -------------------
    # *************** 种类统计 **************
    category_info = list()
    category_type = bc.get_id_list()
    for c_type in category_type:
        info = dict()
        info["name"] = c_type.get("name")
        info["value"] = bro_obj.filter(category=c_type.get("id")).count()
        category_info.append(info)
    # ************* 数据综合 *************
    con = dict()
    con["category"] = category_info
    return con


def get_heatmap_data():
    """
    获取热力图数据，并更新redis
    :return:
    """
    heat_map_data.delay()
    # --------------- 准备 -----------------
    # ********** 当前日期 ***********
    date = d.datetime.now()
    # ********** 序列化器 ***********
    s = serBlackRecord()
    # ********** 查询集 *************
    bro_obj = list(s.get_info_obj().filter(time__year=date.year, time__month=date.month).values("lnglat"))
    # ---------------- 组织数据 ----------------
    lnglat_list = list()
    for bro in bro_obj:
        lnglat = bro.get("lnglat").split(",")
        info = dict()
        info["lng"] = lnglat[0]
        info["lat"] = lnglat[1]
        info["count"] = 1
        lnglat_list.append(info)
    con = {
        "location_list": lnglat_list
    }
    return con
