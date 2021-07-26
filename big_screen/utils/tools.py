# 版本v1.0
import calendar
import configparser
import datetime
import json
import logging
import os
import random
import re
import jsonpath
import requests
from math import radians, cos, sin, asin, sqrt

from big_screen.utils import sys_setting as code

errlog = logging.getLogger("Process")

try:
    from whiteList.models import WhiteList
except Exception as e:
    errlog.info(repr(e))

try:
    from con_control.models import District
except Exception as e:
    errlog.info(repr(e))

try:
    from con_control.Serialization import serDistrict
except Exception as e:
    errlog.info(repr(e))


# --------------------- 工具 --------------------------
def wh_filter_content(content):
    """
    白名单过滤
    :param content:
    :return:
    """
    wh = GetWhiteList()
    wh_region = GetWhiteList("1")
    dis = serDistrict()
    _content = list()
    for con in content:
        freq = con.get("freq")
        adcode = con.get("adcode")
        select_dict = dict()
        select_dict["adcode"] = [adcode]
        try:
            district = dis.select_info(select_dict)[0]["id"]
        except Exception as e:
            continue
        if freq in wh:
            continue
        in_wh_region = False
        for k, v in wh_region.items():
            if district is k:
                if freq in v:
                    in_wh_region = True
        if in_wh_region:
            continue
        _content.append(con)
    return _content


# --------------------- 格式转换 ---------------------------------
def heat_to_nomal(heatlnglat):
    """
    2020/05/06 转为 2020-05-06 00:00:00
    :param heatlnglat:
    :return:
    """
    if type(heatlnglat) == str:
        date_list = heatlnglat.split("/")
        result = "-".join(date_list)
        result = result + " 00:00:00"
        return result


def get_time(str):
    """
    时间格式化　'20200120.110227'转为'2020-01-20 11:02:27'
    :param str:
    :return:
    """
    # time = '20200120.110227'
    time = str.split('.')
    t_year = time[0][0:4]
    t_mon = time[0][4:6]
    t_day = time[0][6:8]
    date = '-'.join([t_year, t_mon, t_day])
    t_hour = time[1][0:2]
    t_min = time[1][2:4]
    t_sec = time[1][4:6]
    this_time = ":".join([t_hour, t_min, t_sec])
    time = " ".join([date, this_time])
    return time


def get_datetime(time_str, model="0"):
    """
    时间格式化　'20200120.110227'转为'2020-01-20 11:02:27'
    返回一个datetime格式
    """
    if model == "0":
        time_str = get_time(time_str)
    time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return time


def getLocation(str):
    """
    坐标转换116.305593-40.046283转为116.305593,40.046283
    :param str:
    :return:
    """
    n_str = str.split('-')
    return ",".join(n_str)


def NowToStr():
    """
    获取当前时间，并返回一个格式为20200120.114927的字符串
    :return:
    """
    now = datetime.datetime.now()
    year = str(now.year)
    month = str(now.month) if (now.month >= 10) else '0' + str(now.month)
    day = str(now.day) if (now.day >= 10) else '0' + str(now.day)
    hour = str(now.hour) if (now.hour >= 10) else '0' + str(now.hour)
    minute = str(now.minute) if (now.minute >= 10) else '0' + str(now.minute)
    second = str(now.second) if (now.second >= 10) else '0' + str(now.second)
    return year + month + day + "." + hour + minute + second


def freq_sql_to_interface(freq_sql_str):
    """
    频点数据库到接口
    :param freq_sql_str:
    :return:
    """
    if type(freq_sql_str) is str:
        freq = eval(freq_sql_str)
    else:
        freq = freq_sql_str
    if type(freq) == float or type(freq) == int:
        freq = round(freq / 10, 2)
        if isFreqLegal(freq):
            freq = float(freq)
            return freq
        else:
            return 0
    else:
        return 0


def freq_interface_to_sql(freq_interface_str):
    """
    频点接口到数据库
    :param freq_interface_sql:
    :return:
    """
    if type(freq_interface_str) is str:
        freq = eval(freq_interface_str)
    else:
        freq = freq_interface_str
    if type(freq) == float or type(freq) == int:
        if isFreqLegal(freq):
            freq = round(freq * 10, 2)
            freq = float(freq)
            return freq
        else:
            return 0
    else:
        return 0


# ------------------------- 特殊格式转化 -------------------------------


# ------------------------------------------------------------------
def MonthDay(year, month):
    """
    获取某个月的第一天和最后一天，返回由两个datetime.datetime对象组成的元组(start,end)
    :param year:
    :param month:
    :return:
    """
    start = datetime.datetime(year, month, 1)
    day, ThisMonth = calendar.monthrange(year, month)
    end = start + datetime.timedelta(days=ThisMonth)
    return (start, end)


def GetWhiteList(model='all'):
    """
    获取白名单频道
    all为返回通用白名单
    region为返回区域白名单
    :return:
    """
    # 系统所在的行政区
    dis_id = code.CHONGQING
    # -------------------------------- 准备白名单 -------------------------------
    wh_obj = WhiteList.objects.all()
    # --------------------- 通用白名单 ------------------
    if model == 'all':
        wh_obj = wh_obj.filter(district=dis_id).values("freq")
        wh_list = list()
        for freq in wh_obj:
            freq = round(float(freq["freq"]) / 10, 2) * 10
            wh_list.append(freq)
        return wh_list
    # --------------------- 区域白名单 ------------------
    else:
        # ------------------------------ 准备区域信息 -------------------------------
        dis_list = list()  # 二级行政区名单
        dis_sub_list = list()  # 三级行政区名单
        dis_obj = District.objects.filter(superior=dis_id)
        # 组织区域id名单
        for dis in dis_obj:
            dis_list.append(dis.id)
            dis_sub_obj = District.objects.filter(superior=dis.id)
            for dis_sub in dis_sub_obj:
                dis_sub_list.append(dis_sub.id)
        # 总名单
        dis_list.extend(dis_sub_list)
        dis_list.append(dis_id)
        # 白名单字典
        info = dict()
        # 组织数据
        for dis in dis_list:
            wh_sub_obj = wh_obj.filter(district=dis).values("freq")
            if len(wh_sub_obj) > 0:
                info[dis] = list()
                for wh in wh_sub_obj:
                    info[dis].append(round(float(wh['freq']) / 10, 2) * 10)
        return info


base_url = 'http://localhost'


def get(base_url, action_url):
    """
    发送get请求
    :param base_url:
    :param action_url:
    :return:
    """
    full_url = base_url + action_url
    headers = {
        "Content-type": "application/json",
        'Upgrade': 'HTTP/1.1'
    }
    return requests.get(full_url, headers=headers, timeout=1)


def post(base_url, action_url, params):
    """
    发送post请求
    :param base_url:
    :param action_url:
    :param params:
    :return:
    """
    full_url = base_url + action_url
    # 请求头
    headers = {
        "Content-type": "application/json",
        'Upgrade': 'HTTP/1.1'
    }
    return requests.post(full_url, headers=headers, data=json.dumps(params), timeout=1)


def RandomChannel(*args):
    """
    生成随机模拟频点
    :return:
    """
    if (args):
        return round((random.randint(76, 108) + random.randint(0, 10) / 10 + random.randint(0, 10) / 100), 2)
    else:
        return round((random.randint(1, 200) + random.randint(0, 10) / 10 + random.randint(0, 10) / 100), 2)


def RandomLocation(*lnglat):
    """
    在一个矩形框内随机生成坐标，需要两个顶点坐标，返回116.305593-40.046283
    格式的字符串
    :return:
    """
    if lnglat and len(lnglat) == 2:
        lnglat1, lnglat2 = lnglat
    else:
        lnglat1 = '106.218377,29.259242'
        lnglat2 = '107.064325,29.86605'
    new_lng = random.uniform(float(lnglat1.split(',')[0]), float(lnglat2.split(',')[0]))
    new_lat = random.uniform(float(lnglat1.split(',')[1]), float(lnglat2.split(',')[1]))
    return str(round(new_lng, 6)) + '-' + str(round(new_lat, 6))


def ReName(newName):
    """
    打开音频文件并重命名为newName.ogg,返回打开的对象
    :param newName:
    :return:
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    fillName = base_dir + '/static/a.mp3'
    with open(fillName, 'rb') as f:
        errlog.info(f.tell())


def getaddress(lnglat):
    """
    逆地理编码，验证坐标后先使用高德api，异常后再用百度api
    :param lnglat:
    :return:
    """
    try:
        lnglat = str(lnglat)
    except Exception as e:
        raise e
    try:
        content = getAddressByAmp(lnglat)
    except Exception as e:
        raise e
    status = content['status']
    if status == '10003':
        try:
            content = getAddressByBD(lnglat)
        except Exception as e:
            raise e
        return content
    else:
        return content


def getAddressByBD(lnglat):
    """
    获取地址可读信息（通过百度api）
    :return:
    """
    headers = {
        "Content-type": "application/json",
        'Upgrade': 'HTTP/1.1'
    }
    url = 'http://api.map.baidu.com/reverse_geocoding/v3/?'
    lnglat = turnLnglat(lnglat)
    params = {
        'ak': 'Nzvad4qwhyY3QdoXMm0O6ym8KvPBPp9Y',
        'output': 'json',
        'coordtype': 'bd09ll',
        'location': lnglat
    }
    try:
        ret = requests.get(url=url, headers=headers, params=params, timeout=1).text
    except requests.exceptions.ConnectionError as e:
        raise e
    except Exception as e:
        raise e
    ret = eval(ret)
    status = ret['status']

    if status == 0:
        info = ret['result']
        district = info['addressComponent']['district']
        adcode = info['addressComponent']['adcode']
        formatted_address = info['formatted_address']
        data_from = "baidu"
    else:
        district = '获取失败 原因: ' + str(status)
        formatted_address = '获取失败 原因: ' + str(status)
        data_from = "baidu"
        adcode = 0
    content = {
        'status': status,
        'district': district,
        'formatted_address': formatted_address,
        "data_from": data_from,
        "adcode": adcode
    }
    return content


def getAddressByAmp(lnglat):
    """
    逆地理编码，通过高德地图api
    :param lnglat:
    :return:
    """
    key = "efe4e9291a4a665ff691c55e3a3b871d"
    url = "https://restapi.amap.com/v3/geocode/regeo?"

    params = {
        "key": key,
        "location": lnglat
    }
    headers = {
        "Content-type": "application/json",
        'Upgrade': 'HTTP/1.1'
    }
    try:
        ret = requests.get(url=url, headers=headers, params=params, timeout=1).text
    except requests.exceptions.ConnectionError as e:
        raise e
    except Exception as e:
        raise e
    ret = eval(ret)
    infocode = ret['infocode']
    if infocode == '10000':
        info = ret["regeocode"]
        district = info["addressComponent"]["district"]
        adcode = info["addressComponent"]["adcode"]
        formatted_address = info["formatted_address"]
        data_from = "gaode"
    else:
        district = '[g]获取失败 原因: ' + infocode
        formatted_address = '[g]获取失败 原因: ' + infocode
        data_from = "gaode"
        adcode = 0
    content = {
        'status': infocode,
        "district": district,
        "formatted_address": formatted_address,
        "data_from": data_from,
        "adcode": adcode
    }
    return content


def turnLnglat(lnglat):
    """
    转化坐标系，国测坐标系转换为百度坐标系,经纬度转置
    :param lnglat:
    :return:
    """
    url = 'http://api.map.baidu.com/geoconv/v1/'
    headers = {
        "Content-type": "application/json",
        'Upgrade': 'HTTP/1.1'
    }
    params = {
        'coords': lnglat
        , 'ak': 'Nzvad4qwhyY3QdoXMm0O6ym8KvPBPp9Y'
        , 'from': "3"
        , 'to': "5"
    }
    try:
        ret = requests.get(url=url, headers=headers, params=params, timeout=1).text
    except requests.exceptions.ConnectionError as e:
        raise e
    except Exception as e:
        raise e
    ret = eval(ret)
    try:
        x = round(float(ret['result'][0]['x']), 6)
        y = round(float(ret['result'][0]['y']), 6)
        lnglat = str(y) + ',' + str(x)
    except Exception as e:
        raise e

    return lnglat


def getNameFromAdcode(adcode):
    """
    根据adcode(行政区编码)获取下级行政区名称
    :param adcode:
    :return:
    {'name': ['北京市'],
 'sub': ['东城区',
  '西城区',
  '朝阳区',
  '丰台区',
  '石景山区',
  '海淀区',
  '门头沟区',
  '房山区',
  '通州区',
  '顺义区',
  '昌平区',
  '大兴区',
  '怀柔区',
  '平谷区',
  '密云区',
  '延庆区']}
    """
    url = 'https://webapi.amap.com/ui/1.0/ui/geo/DistrictExplorer/assets/d_v1/country_tree.json'
    headers = {
        "Content-type": "application/json",
        'Upgrade': 'HTTP/1.1'
    }
    ret = requests.get(url, headers=headers, timeout=1)
    data = json.loads(ret.text)
    content = dict()
    content['name'] = jsonpath.jsonpath(data, '$.children[?(@.adcode==' + str(adcode) + ')].name')
    content['center'] = jsonpath.jsonpath(data, '$.children[?(@.adcode==' + str(adcode) + ')].center')
    content['sub'] = jsonpath.jsonpath(data, '$.children[?(@.adcode==' + str(adcode) + ')].children[*].name')
    return content


def isFreqLegal(freq):
    """
    判断频点是否合法
    :param freq:
    :return:
    """
    return 76 <= float(freq) <= 108


def test_celery():
    """
    动态修改celery动态定时
    :return:
    """
    from djcelery.models import CrontabSchedule
    from djcelery.schedulers import DatabaseScheduler
    crontab = CrontabSchedule.objects.create(
        hour='*',
        minute='*/2',
        day_of_week='*',
        day_of_month='*',
        month_of_year="*"
    )
    schedule = crontab.schedule

    create_or_update_tast = DatabaseScheduler.create_or_update_task
    task_template = 'con_setting.tasks.fun_text'
    task_name = 't_task'
    schedule_dict = {
        'schedule': schedule,
        'args': list(),
        'task': task_template,
        'enabled': 1
    }
    create_or_update_tast(task_name, **schedule_dict)


def delete_celery_task(task_name):
    from djcelery.schedulers import DatabaseScheduler
    DatabaseScheduler.delete_task(task_name)


def haversine(p1, p2):
    """
    计算两个坐标之间的距离，单位:米
    :param p1: 字符串
    :param p2: 字符串
    :return:
    """
    lng1, lat1 = p1.split(',')
    lng2, lat2 = p2.split(',')
    lng1, lat1, lng2, lat2 = map(float, [lng1, lat1, lng2, lat2])
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # 地球平均半径，单位为公里
    return round(c * r * 1000, 0)


# -------------------- 根据id检索orm ----------------------
def select_mobile_by_id(mobile_id):
    """
    返回手机名称
    :param mobile_id:
    :return:
    """
    pass


# ------------------- 类 -----------------------------
class MakeDistrict:
    def __init__(self):
        from con_control.Serialization import serDistrict
        self.data = self.get_district_info()
        self.s = serDistrict()

    def unknow_district(self):
        """
        填充未知行政区
        :return:
        """
        try:
            self.s.table.get(adcode=code.UNKNOW)
        except self.s.table.model.DoesNotExist:
            sub = dict()
            sub["name"] = "未知"
            sub["adcode"] = code.UNKNOW
            self.insert_to_sql(sub, 0)

    def province_district(self):
        """
        填充省级行政区
        :return:
        """
        sub_info = self.data.get("children")
        for sub in sub_info:
            self.insert_to_sql(sub, 0)

    def city_district(self, adcode):
        """
        填充市级行政区
        :param adcode:所在省的行政区编码
        :return:
        """
        # 组织数据
        info = jsonpath.jsonpath(self.data, '$.children[?(@.adcode==' + str(adcode) + ')]')[0]  # 省级行政区
        try:
            obj = self.s.table.get(adcode=adcode)
        except District.DoesNotExist:
            self.insert_to_sql(info, 0)
            obj = self.s.table.get(adcode=adcode)
        # 市级行政区
        sub_info = info.get("children")
        for sub in sub_info:
            self.insert_to_sql(sub, obj.id)

    def tg_district(self, adcode):
        """
        填充台站,每个城市一个台站
        :param adcode:
        :return:
        """
        # 组织数据
        info = jsonpath.jsonpath(self.data, '$.children[?(@.adcode==' + str(adcode) + ')]')[0]  # 省级行政区
        # 省级单位
        try:
            obj = self.s.table.get(adcode=adcode)
        except District.DoesNotExist:
            self.insert_to_sql(info, 0)
            obj = self.s.table.get(adcode=adcode)
        # 城市信息
        sub_info = info.get("children")
        for sub in sub_info:
            sub_adcode = sub.get("adcode")
            # 城市对象
            try:
                sub_obj = self.s.table.get(adcode=sub_adcode)
            except self.s.table.model.DoesNotExist:
                self.insert_to_sql(sub, obj.id)
                sub_obj = self.s.table.get(adcode=sub_adcode)
            self.insert_tg_to_sql(sub, sub_obj.id)

    def addTG(self, adcode):
        """
        添加台站
        :param adcode:
        :return:
        """
        dis = serDistrict()
        disId = dis.table.get(is_district=1, adcode=adcode).id
        subDis = dis.table.filter(is_district=1, superior=disId)
        for sub in subDis:
            tgInfo = {
                "is_district": 0,
                "name": sub.name,
                "adcode": sub.adcode,
                "superior": sub.superior
            }
            tg = dis.table.create(**tgInfo)
            tg.save()

    def dis_district(self, adcode):
        """
        填充区县级行政区
        """
        # 组织数据
        info = jsonpath.jsonpath(self.data, '$.children[?(@.adcode==' + str(adcode) + ')]')[0]  # 省级行政区
        # 市级数据
        sub_info = info.get("children")
        for sub in sub_info:
            # 区县级数据
            sub_sub_info = sub.get("children")
            for sub_sub in sub_sub_info:
                city_id = self.s.table.get(adcode=sub_sub.get("cityCode")).id
                self.insert_to_sql(sub_sub, city_id)

    def select_adcode(self, adcode):
        info = jsonpath.jsonpath(self.data, '$.children[?(@.adcode==' + str(adcode) + ')]')[0]
        sub_info = info.get("children")
        return sub_info

    def insert_tg_to_sql(self, info_dict, superior):
        """
        将台站加入数据库
        :param info_dict:
        :param superior:
        :return:
        """
        insert_dict = dict()
        insert_dict["name"] = info_dict.get("name")
        insert_dict["adcode"] = info_dict.get("adcode")
        insert_dict["superior"] = superior
        insert_dict["is_district"] = 0
        try:
            obj = self.s.table.get(adcode=insert_dict["adcode"], is_district=0)
        except self.s.table.model.DoesNotExist:
            self.s.insert_info(**insert_dict)
        else:
            insert_dict["id"] = obj.id
            self.s.update_info(insert_dict)

    def insert_to_sql(self, info_dict, superior):
        """
        插入数据库
        :return:
        """
        insert_dict = dict()
        insert_dict["name"] = info_dict.get("name")
        insert_dict["adcode"] = info_dict.get("adcode")
        insert_dict["superior"] = superior
        try:
            obj = self.s.table.get(adcode=insert_dict["adcode"], is_district=1)
        except District.DoesNotExist:
            self.s.insert_info(**insert_dict)
        else:
            insert_dict["id"] = obj.id
            self.s.update_info(insert_dict)

    def get_district_info(self):
        """
        获取原始数据
        :return:
        """
        url = 'https://webapi.amap.com/ui/1.0/ui/geo/DistrictExplorer/assets/d_v1/country_tree.json'
        headers = {
            "Content-type": "application/json",
            'Upgrade': 'HTTP/1.1'
        }
        ret = requests.get(url, headers=headers, timeout=1)
        data = json.loads(ret.text)
        return data


class setting():
    def __init__(self):
        """
        设置配置文件，可修改系统开始检测的日期、黑广播检索时间
        此处为构造函数
        """
        self.config = configparser.ConfigParser()
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.config.read(self.path + '/time.ini')
        # 系统起始时间
        self.start_time = self.config.get('time', 'start_time')
        self.today = datetime.datetime.today()
        # 首页黑广播展示时间范围
        self.timerange = self.config.get('time', 'timerange')
        # 周期
        self.chart_selectcycle = int(self.config.get('time', 'chart_selectcycle'))
        self.massmark_selectcycle = int(self.config.get('time', 'massmark_selectcycle'))
        self.isworking_selectcycle = int(self.config.get('time', 'isworking_selectcycle'))

    def set(self, key, value):
        value = int(value)
        if key == "chart":
            if 24 >= value >= 1:
                self.config.set('time', 'CHART_SELECTCYCLE', str(value))
            else:
                return '更新周期范围为[1,24]小时'
        elif key == "broad":
            if 300 >= value >= 5:
                self.config.set('time', 'MASSMARK_SELECTCYCLE', str(value))
            else:
                return '更新周期范围为[5,300]秒'
        elif key == "isworking":
            if 300 >= value >= 5:
                self.config.set('time', 'ISWORKING_SELECTCYCLE', str(value))
            else:
                return "更新周期范围为[5,300]秒"
        else:
            return "没有该设置项"
        try:
            with open(self.path + '/time.ini', 'w+') as f:
                self.config.write(f)
        except Exception as e:
            errlog.info(repr(e))
            return '保存失败'
        return "ok"

    def save(self):
        """
        保存系统起始时间
        :return:
        """
        if self.start_time == '':
            self.start_time = str(self.today)
            self.config.set('time', 'start_time', self.start_time)
            try:
                with open(self.path + '/time.ini', 'w+') as f:
                    self.config.write(f)
            except Exception as e:
                errlog.info(repr(e))

    def get_datediff(self):
        """
        获取系统检测天数
        :return:
        """
        self.save()
        fmt = '%Y-%m-%d'
        now = datetime.datetime.strptime(self.start_time, fmt)
        start_time = now
        date_diff = self.today.__sub__(start_time)
        return date_diff.days

    def get_timeRange(self):
        """
        获取时间范围
        :return:
        """
        return int(self.timerange) * 60

    def get_timerange(self):
        """
        获取时间范围(页面用)
        :return:
        """
        return int(self.timerange)

    def save_timeRange(self, num):
        num = str(num)
        self.config.set('time', 'timeRange', num)
        with open(self.path + '/time.ini', 'w') as f:
            self.config.write(f)

        self.timerange = num
        return 0

    def getStartDay(self):
        """
        获取系统开始的时间
        :return:
        """
        return self.start_time

    def getStartDay_datetime(self):
        """
        获取系统开始时间，返回一个datatime
        :return:
        """
        return datetime.datetime.strptime(self.start_time + " 00:00:00", code.DATA_FORMATTER)
