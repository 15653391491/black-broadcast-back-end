from big_screen.utils.start_sys import start_sys
from big_screen.serialization import allSerialization as alls


def init():
    st = start_sys()
    st.init_monitor()
    st.init_mobile()
    st.init_whcategory()
    st.init_blackcategory()
    st.init_district()


def make():
    make_freq()


def make_freq():
    """
    修正频点
    :return:
    """
    wl = alls.serWhiteList()
    br = alls.serBlackRecord()
    wl.make_freq()
    br.make_freq()


def make_wlcategory():
    """
    修正频点类型
    :return:
    """
    wl = alls.serWhiteList()
    wl.make_whcategory_normal()


def make_brislegal():
    """
    修正黑广播合法
    :return:
    """
    br = alls.serBlackRecord()
    # br.make_district()
    br.make_islegal()


def make_bc():
    br = alls.serBlackRecord()
    br.make_blackCategory()


def demo():
    br = alls.serBlackRecord()
    br.make_freq()
