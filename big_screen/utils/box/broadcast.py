from django_redis import get_redis_connection
import json

from big_screen.utils import tools as t

try:
    from con_brocast.models import BlackCategory
except Exception as e:
    print(e)


def broadcast_to_redis(bro_list):
    """
    将黑广播进行白名单过滤、处理存入redis中海量点、热力图、
    轮播表的队列中．
    :param bro_list:
    :return:
    """
    # ---------------- 验证 --------------------------
    if type(bro_list) is not list:
        return '需要输入黑广播列表'
    # ---------------- 建立连接 ----------------------
    massmark_con = get_redis_connection('massmark')
    bro_con = get_redis_connection('broadcast')
    # 广播种类
    category_obj = BlackCategory.objects.all()
    # 坐标
    info = bro_list[0]
    lnglat_str = t.getLocation(info['location'])
    # ---------------- 组织数据 ----------------------
    for b_d in bro_list:
        # ------------------------ 组织数据 ---------------------------------------
        time = t.get_time(b_d['time'])  # 时间
        freq = round(float(b_d['freq']) / 10, 2)  # 频点
        category = category_obj.get(num=b_d['category'])['Name']  # 种类
        lnglat = lnglat_str.split(',')
        address = t.getaddress(lnglat_str)['formatted_address']
        # -------------------------- massmark缓存 --------------------------------------
        mass_message = dict()
        mass_message['Channel'] = freq
        mass_message['Time'] = time
        mass_message['Category__Name'] = category
        massmark_con.lpush(lnglat_str, json.dumps(mass_message))
        # --------------------------- 热力图缓存 ----------------------------------------
        heat_message = dict()
        heat_message['lng'] = lnglat[0]
        heat_message['lat'] = lnglat[1]
        heat_message['count'] = 1
        heat_message['time'] = time
        bro_con.lpush('heatmap_n', json.dumps(heat_message))
        # --------------------------- 轮播表缓存 ----------------------------------------
        scroll_message = list()
        scroll_message.append(time)
        scroll_message.append(freq)
        scroll_message.append(category)
        scroll_message.append(address)
        print(address)
        bro_con.lpush('scroll_n', json.dumps(scroll_message))
    # ------------------------------ 结束 -----------------------------------------------
    return '缓存成功'
