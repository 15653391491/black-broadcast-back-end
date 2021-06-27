#!/usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import
from big_screen.utils import tools as t
import calendar
import datetime

from con_brocast.models import BlackCategory
from big_screen.celery import app
from con_brocast.Serialization import serBlackRecord
from big_screen.redisOpration.AllOpration import chartOp, broadcastOp, massmarkOp
from con_control.Serialization import serMobile
from big_screen.serialization.allSerialization import serUserRecord,serBlackRecord


@app.task
def set_bigscreen_chart():
    """
    定时更新redis中的图表数据（近一段时间）,包括：
    1.右上角的计数器１．检测天数２．黑广播数３．移动端设备数量
    2.年统计表、月统计表(今年各个月份黑广播数量与本月每天的黑广播数量)
    3.种类统计表，获取种类名称列表和各种类数量
    4.日统计，统计今年各个时间段中黑广播数量分布
    :return:
    """
    # -------------- 基础查询 -------------
    # ********* 序列化器 *********
    bro = serBlackRecord()  # 黑广播
    mob = serMobile()  # 检测设备
    # ********* 查询集 *************
    bro_obj = bro.get_info_obj()
    # ************* redis ***************
    chart_con = chartOp()
    # --------------------- 一、右上角的计数器１．检测天数２．黑广播数３．移动端设备数量 ------------------
    # **************** 检测天数 ****************
    gt = t.setting()
    date_diff = gt.get_datediff()
    # **************** 黑广播数 ****************
    bro_num = bro_obj.count()
    # **************** 检测设备数 ***************
    mo_num = mob.table.filter(is_delete=0).count()
    # **************** 组织数据 ******************
    con_counter = {
        'date_diff': date_diff,
        'blackbrocast': bro_num,
        'MobileNum': mo_num
    }
    # ------------------------- 二、年统计与月统计 ---------------------------------
    this_year = datetime.date.today().year
    this_month = datetime.date.today().month
    # **************** 黑广播年统计 ******************
    y_data = list()
    m_data = list()
    monthrange = calendar.monthrange(this_year, this_month)[1]
    # **************** 广播查询集 ******************
    bro_obj_year = bro_obj.filter(time__year=this_year)
    for i in range(12):
        y_data.append(bro_obj_year.filter(time__month=i + 1).count())
    bro_obj_month = bro_obj_year.filter(time__month=this_month)
    for i in range(monthrange):
        m_data.append(bro_obj_month.filter(time__day=i + 1).count())
    # **************** 组织数据 **********************
    chart_year_month = {
        'y_data': y_data,
        'm_data': m_data
    }
    # --------------------------- 三、种类表，获取种类名称和各种类数量 -------------------------------------
    # ************** 种类列表 *****************
    category_obj = BlackCategory.objects.all().values('name')
    categorylist = list()
    # ************ 标签 ***************
    legend = list()
    for category in category_obj:
        categorylist.append({
            'name': category['name'],
            'value': bro_obj.filter(category__name=category['name']).count()
        })
        legend.append(category['name'])
    category = {
        'legend': legend,
        'category': categorylist
    }
    # -------------------------- 四、时间统计，统计今年黑广播的各时间段分布 ---------------------------
    # ********** 结果 ************
    time_list = list()
    for i in range(23):
        time_list.append(bro_obj_year.filter(time__hour=i).count())
    time_count = {
        'time_list': time_list
    }
    # ------------------------ 五、打卡排名 ------------------------------
    ur = serUserRecord()
    urqueryset = ur.summaryByColumn("mobile__name")
    chartUserRecord = ur.queryToList(urqueryset.order_by("-count"))
    # ------------------------ 六、黑广播发现排名 ------------------------------
    br = serBlackRecord()
    brSummary = br.summaryByRegion()
    # ------------------------- 设置redis ----------------------------
    # ************* 计数器 ***************
    chart_con.kv_set("counter", con_counter)
    # ************* 年统计月统计 **************
    chart_con.kv_set("chart_year_month", chart_year_month)
    # *************** 种类列表与数量字典 *******************
    chart_con.kv_set("category", category)
    # **************** 时间统计 *******************
    chart_con.kv_set("time_count", time_count)
    # *************** 打卡记录统计 *****************
    chart_con.kv_set("mobileSummary", chartUserRecord)
    # *************** 黑广播发现地区统计 *****************
    chart_con.kv_set("regionSummary", brSummary)



@app.task
def set_black_broadcasting():
    """
    触发式保存redis中的海量点、热力图、轮播表
    :return:
    """
    # ------------ 准备 ----------------
    # *********** 时间范围 **********
    s = t.setting()  # 时间范围
    timerange = s.get_timeRange()
    e_time = datetime.datetime.now()
    s_time = e_time - datetime.timedelta(minutes=timerange)
    # *********** 序列化器 **********
    bro = serBlackRecord()
    # *********** redis *************
    bro_con = broadcastOp()
    mass_con = massmarkOp()
    # *********** 查询集 *************
    select_dict = dict()
    select_dict["s_time"] = s_time
    select_dict["e_time"] = e_time
    content = bro.select_info(select_dict)
    # ---------------- 组织缓存数据 ----------------------
    # ********** 海量点 ************
    mass_content = list(map(mass_con.formatter_data_from_ser, content))
    # ********** 轮播表 ************
    scroll_content = list(map(bro_con.formatter_scroll_info_from_ser, content))
    # ********** 热力图 ************
    heatmap_content = list(map(bro_con.formatter_heatmap_info, content))
    # -------------------- 存入redis ------------------
    # ********** 海量点 *************
    mass_con.flush_db()  # 清空数据
    for con in mass_content:
        k, v = con
        mass_con.list_push(k, v)
    # *********** 轮播表 ***********
    bro_con.del_key("scroll_n")
    for con in scroll_content:
        bro_con.list_push("scroll_n", con)
    # *********** 热力图 ***********
    bro_con.del_key("heatmap_n")
    for con in heatmap_content:
        bro_con.list_push("heatmap_n", con)
