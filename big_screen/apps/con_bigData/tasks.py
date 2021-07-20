import datetime as d
from time import clock
import logging

from big_screen.celery import app
from big_screen.utils import tools as t
from big_screen.serialization.allSerialization import serBlackRecord, serBlackCategory
from big_screen.redisOpration.AllOpration import broadcastOp

errlog = logging.getLogger("Process")


@app.task
def save_chart_data():
    """
    保存控制中心的图表信息
    :return:
    """
    getChartData()

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
    return con


def getChartData():
    """
    获取图表统计数据
    :return:
    """
    # -------------- 操作类 -----------------
    # ********** 数据库 *************
    br = serBlackRecord()  # 黑广播
    bc = serBlackCategory()  # 广播类型
    # ********** redis *************
    broOp = broadcastOp()
    # ********** 配置文件 ***********
    settings = t.setting()
    # -------------- 查询 -----------------
    # ********* 时间范围 ***********
    today = d.datetime.now()  # 当前时间
    startTime = settings.getStartDay_datetime()  # 系统起始时间
    dayRange = today - startTime  # 时间范围

    # ********* 每日统计 ************
    def countForDays(i):
        start = startTime + d.timedelta(days=i)
        end = start + d.timedelta(days=1)
        select_info = {
            "islegal": 0,
            "time__gte": start,
            "time__lt": end
        }
        result = br.select(select_dict=select_info)
        return result.count()

    summaryForDays = [info for info in map(countForDays, [x for x in range(dayRange.days + 1)])]
    summaryForDays.reverse()

    # *********** 年统计 **************
    def countForYear(i):
        select_info = {
            "islegal": 0,
            "time__month": i,
        }
        result = br.select(select_dict=select_info)
        return result.count()

    summaryForYear = [info for info in map(countForYear, [x for x in range(13) if x != 0])]

    # ********* 月统计 ****************
    def countForMonth(i):
        select_info = {
            "islegal": 0,
            "time__day": i,
        }
        result = br.select(select_dict=select_info)
        return result.count()

    summaryForMonth = [info for info in map(countForMonth, [x for x in range(32) if x != 0])]

    # ********** 日统计 ***************
    def countForTime(i):
        select_info = {
            "islegal": 0,
            "time__hour": i,
        }
        result = br.select(select_dict=select_info)
        return result.count()

    summaryForTime = [info for info in map(countForTime, [x for x in range(24)])]

    # ********** 种类统计 ***************
    def countForCategory(type):
        select_info = {
            "islegal": 0,
            "category": type.get("id"),
        }
        result = br.select(select_dict=select_info).count()
        return {
            "name": type.get("name"),
            "value": result
        }

    categoryType = bc.get_id_list()
    summaryForCategory = [info for info in map(countForCategory, [x for x in categoryType])]
    # ------------------- 保存redis ---------------------
    content = {
        "data_list": summaryForDays,
        "year_count": summaryForYear,
        "month_count": summaryForMonth,
        "day_count": summaryForTime,
        "category": summaryForCategory,
    }
    broOp.kv_set("chart_data", content)
    return content


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
