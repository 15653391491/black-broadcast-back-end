import time
import threading
import random
import os
import logging
import json
import datetime
import requests
from logging import handlers
from big_screen.utils import tools as t

basepath = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

today = datetime.datetime.now().strftime('%Y-%m-%d')
logPath = basepath + '/log/' + today + '.log'
filePath = os.path.dirname(os.path.abspath(__file__)) + '/a.ogg'

h = handlers.TimedRotatingFileHandler
Handel = logging.FileHandler(filename=logPath)
Fommat = logging.Formatter(fmt='%(asctime)s %(name)s %(message)s', datefmt='%Y-%m-%d-%H-%M-%S')
Handel.setFormatter(Fommat)


def hblog(msg):
    """
    记录心跳包日志
    :param msg:
    :return:
    """
    log = logging.getLogger('Heartbeat')
    log.setLevel(logging.INFO)
    # 加线程锁
    lock = threading.Lock()
    lock.acquire()
    log.addHandler(Handel)
    log.info(msg)
    log.removeHandler(Handel)
    lock.release()
    # 释放
    return 'log Heartbeat'


def brlog(msg):
    """
    黑广播信息记录
    :param msg:
    :return:
    """
    log = logging.getLogger('Broadcasting')
    log.setLevel(logging.INFO)
    # 加线程锁
    lock = threading.Lock()
    lock.acquire()
    log.addHandler(Handel)
    log.info(msg)
    log.removeHandler(Handel)
    lock.release()
    # 线程释放
    return 'log Broadcasting'


def hberr(msg):
    """
    心跳包返回错误记录
    :return:
    """
    log = logging.getLogger('hberr')
    log.setLevel(logging.INFO)
    # 加线程锁
    lock = threading.Lock()
    lock.acquire()
    log.addHandler(Handel)
    log.info(msg)
    log.removeHandler(Handel)
    lock.release()
    # 线程释放
    return 'log hberr'


def brerr(msg):
    """
    心跳包返回错误记录
    :return:
    """
    log = logging.getLogger('brerr')
    log.setLevel(logging.INFO)
    # 加线程锁
    lock = threading.Lock()
    lock.acquire()
    log.addHandler(Handel)
    log.info(msg)
    log.removeHandler(Handel)
    lock.release()
    # 线程释放
    return 'log brerr'


class Phone():
    def __init__(self, phoneid):
        self.phoneid = phoneid
        self.category = ['0', '1', '2', '3', '4', '5']
        # self.baseurl = 'http://localhost'
        self.baseurl = 'http://116.171.245.2:3085'
        # self.baseurl = 'http://47.97.250.65'
        # self.baseurl = 'http://123.147.192.156:18888'

    def GetWhitelist(self):
        """
        获取白名单
        :return:
        """
        action_url = '/d/whitelist'
        try:
            ret = t.get(self.baseurl, action_url)
        except Exception:
            return '接口错误'
        # for item, value in ret:
        return eval(ret.content.decode())

    def PostWhiteList(self):
        """
        发送白名单
        :return:
        """
        action_url = '/d/whitelist'
        params = {
            'time': t.NowToStr(),
            'data': [{
                'freq': t.RandomChannel(),
                'name': '北京交通台'
            }]
        }
        ret = t.post(self.baseurl, action_url, params)
        try:
            return eval(ret.content.decode())
        except SyntaxError as e:
            return (e, ret)
        except Exception as e:
            return e

        # return ret.content.decode()

    def Heartbeat(self, location):
        """
        模拟心跳包
        :return:
        """
        action_url = '/d/isworking'
        heartbeat = {
            'phoneid': self.phoneid,
            'location': location,
            # 'location': t.RandomLocation('116.096295,40.513769', '116.854351,39.740956'),
            'time': t.NowToStr()
        }
        hblog(json.dumps(heartbeat))
        # logging.info(json.dumps(heartbeat))
        try:
            ret = t.post(self.baseurl, action_url, heartbeat)
        except SyntaxError as e:
            # hberr(e)
            return 'none'
        except Exception as e:
            # hberr(e)
            return 'none'
        try:
            info = eval(ret.content.decode())
            # hberr(info)
        except Exception as e:
            pass
            # hberr(e)
        # time.sleep(2)

    def BlackRecord(self, location):
        action_url = '/d/broadcast/text'
        # location = t.RandomLocation('116.096295,40.513769', '116.854351,39.740956')
        # location = t.RandomLocation('108.406604,31.435889', '109.318469,30.749114')
        freq = round(t.RandomChannel(1) * 10, 2)

        time = t.NowToStr()
        record = '_'.join([str(freq), time, location, '136000'])  # 频率_时间_坐标_时长.ogg
        # self.Record(record + '.ogg')
        params = {
            'data': [{
                'category': random.choice(self.category),
                'phoneid': self.phoneid,
                'location': location,
                'freq': freq,
                'time': time,
                'record': record,
                'acquisitionmode': '0',
                'confidencelevel': '50',
                'contact': '15653391491',
                'common': 'yingbatian'
            }]
        }
        brlog(json.dumps(params))
        # logging.info(params)
        try:
            ret = t.post(self.baseurl, action_url, params)
            print(str(ret) + '黑广播')
        except Exception as e:
            print(repr(e))
            # ret="x"
            # print(str(ret) + '黑广播')
            # pass
            # # brerr(e)
        else:
            try:
                info = eval(ret.content.decode())
                # brerr(info)
            except SyntaxError as e:
                pass
                # brerr(e)
            except Exception as e:
                pass
                # brerr(e)

    def Record(self, record):
        action_url = '/d/record'
        files = {
            'name': (record, open(filePath, 'rb'))
        }
        ret = requests.post(self.baseurl + action_url, files=files)
        print(str(ret) + '音频')


class myThread(threading.Thread):
    def __init__(self, threadID, name, counter, phoneid):
        """
        构造函数
        :param threadID:
        :param name:
        :param counter:
        """
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.phoneid = phoneid

    def run(self):
        while self.counter:
            print('开始线程: ' + self.name)
            # location = t.RandomLocation('108.406604,31.435889', '109.318469,30.749114') # 重庆
            location = t.RandomLocation('105.778698,27.369509', '108.261608,26.310833') # 贵州
            # location = t.RandomLocation('105.489591,37.408711', '106.522306,36.93599')
            # location = t.RandomLocation('106.100109,27.501978', '107.934826,25.931906')
            p = Phone(self.phoneid)
            p.Heartbeat(location)
            p.BlackRecord(location)
            print('线程结束: ' + self.name)
            time.sleep(5)
            self.counter -= 1


if __name__ == '__main__':
    th1 = myThread(1, 'th1', 4, '865267021777652')  # aaa
    th2 = myThread(1, 'th2', 4000, '865267021777653')  # asasa
    th3 = myThread(1, 'th3', 4000, '865267021777650')  # o
    th4 = myThread(1, 'th4', 4000, '865267021777651')  # o
    th5 = myThread(1, 'th5', 4000, '865267021777611')  # o
    # th6 = myThread(1, 'th6', 100000, 'a1084892064')  # o
    th1.start()
    th2.start()
    th3.start()
    th4.start()
    th5.start()
    # th6.start()
