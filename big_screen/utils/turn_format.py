import calendar
import datetime

from big_screen.utils import re_format as f


# ----------- 时间转换 -----------------
class time_formatter:
    def __init__(self):
        self.now_time = datetime.datetime.now()
        self.now_time_str = self.now_time.strftime(f.DATA_FORMATTER)

    @classmethod
    def get_time_heat(cls, heatlnglat):
        """.
        热力图时间选择器时间格式转换
        2020/05/06 转为 2020-05-06 00:00:00
        :param heatlnglat:
        :return:
        """
        if type(heatlnglat) == str:
            date_list = heatlnglat.split("/")
            result = "-".join(date_list)
            result = result + " 00:00:00"
            return result

    @classmethod
    def get_time_str(cls, str):
        """
        时间格式化　'20200120.110227'转为'2020-01-20 11:02:27'
        返回str
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

    @classmethod
    def get_time_datetime(cls, time_str, model="0"):
        """
        时间格式化　'20200120.110227'转为'2020-01-20 11:02:27'
        返回一个datetime格式
        """
        if model == "0":
            time_str = cls.get_time_str(time_str)
        time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        return time


class lnglat_formatter:
    @classmethod
    def get_lnglat(cls, str):
        """
        坐标转换116.305593-40.046283转为116.305593,40.046283
        :param str:
        :return:
        """
        n_str = str.split('-')
        result = ",".join(n_str)
        return result


class freq_formatter:

    @classmethod
    def isFreqLegal(cls, freq):
        """
        判断频点是否合法
        :param freq:
        :return:
        """
        # 转格式
        return 76 <= float(freq) <= 108

    @classmethod
    def mobile_to_django(cls, freq):
        """
        手机到平台的频点转换，频点除以10保留两位数并转化为float类型
        :param freq:
        :return:
        """
        # 转格式
        if type(freq) is str:
            freq = eval(freq)
        return float(round(freq / 10, 2))


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


# ------------------------- 结果转换 --------------------------------
class formatterReturn:
    def __init__(self):
        pass

    def get_whitelist(self, content):
        """
        # a = {
        #     "data": [
        #         {
        #             "district": 2,
        #             "time": "2020-05-25 00:00:00",
        #             "freq": 88.6,
        #             "type": 2,
        #             "id": 129,
        #             "name": "测试频点二"
        #         }
        #     ],
        #     "msg": "success",
        #     "count": 10,
        #     "code": 0
        # }
        # b = {
        #     "data": {
        #         "list": [{
        #             "freq": 92.7,
        #             "name": "\u9891\u90533"
        #         }],
        #         "count": 6,
        #         "this_page_num": 1,
        #         "num_pages": 1
        #         },
        #     "errmsg": "success",
        #     "errno": 10000
        # }
        :param content:
        :return:
        """
        _content = dict()
        _content["errmsg"] = "success"
        _content["errno"] = 10000
        data = dict()
        data["this_page_num"] = 1
        data["num_pages"] = 1
        data["list"] = list()
        for con in content["data"]:
            info = dict()
            info["freq"] = float(con.get("freq"))
            info["name"] = con.get("name")
            info["type"] = con.get("type")
            info["time"] = con.get("time")
            info["district"] = con.get("district")
            data["list"].append(info)
        data["count"] = len(data["list"])
        _content["data"] = data
        return _content
