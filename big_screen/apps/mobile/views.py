from django.views import View
from django.http import JsonResponse, FileResponse
import traceback
import re
import os
import logging

from big_screen.utils import sys_setting as code
from big_screen.serialization.allSerialization import serMobileVersion, serMobile, serMonitor, serUserRecord, \
    serWhiteList, serWhiteCategory, serDistrict, serBlackRecord, serRedioTest, serBlackCategory, serPlatform, \
    serMobileToPlatform
from big_screen.utils import re_format as f
from big_screen.utils.turn_format import lnglat_formatter, time_formatter, formatterReturn, freq_formatter
from big_screen.redisOpration.AllOpration import isworkingOp, massmarkOp, broadcastOp, whdisOp
from con_brocast.tasks import save_to_mysql
from big_screen.utils import tools as t

# ------------- 日志器 --------------------
# 录音
recordLogger = logging.getLogger("record")
brlog = logging.getLogger("Broadcasting")
moblog = logging.getLogger("mobile")
relog = logging.getLogger("request")
errlog = logging.getLogger("Process")


# Create your views here.
# 版本
class versionView(View):

    @classmethod
    def post(cls, request):
        try:
            # --------------- 接收 ------------------
            ret = request.body.decode()
            # ******** 是否收到请求体中的数据 **********
            if ret is "":
                ret = {
                    "time": "",
                    "location": "",
                    "phoneid": "",
                    "version": ""
                }
            else:
                ret = eval(ret)
            relog.info("getversion " + str(ret))
            # *********** 取数据 **************
            time = ret.get("time")
            mobile = ret.get("phoneid")
            version = ret.get("version")
            # --------------- 验证 -----------------
            time_result = re.fullmatch(f.DATE_FORMATTER_RE_PHONE, time)
            mobile_result = re.fullmatch(f.PHONEID_FORMATTER_RE, mobile)
            # --------------- 处理 -----------------
            # ******** 格式转化器 ********
            tf = time_formatter()
            # ******** 序列化器 ********
            mv = serMobileVersion()
            # ******** 时间处理 *********
            if time_result is None:
                time = tf.now_time_str
            else:
                time = tf.get_time_str(time)
            # ********* 手机id处理 *********
            if mobile_result is None:
                mobile = f.UNKNOW_MOBILE
            mob_id = mv.mob.get(mobile=mobile).id
            # ********* 结果组织 ***********
            insert_dict = dict()
            insert_dict["time"] = time
            insert_dict["version"] = version
            insert_dict["mobile"] = mob_id
            # *********** 更新数据库 **************
            try:
                v_id = mv.table.get(mobile=mob_id).id
            except mv.table.model.DoesNotExist:
                mv.insert_info(**insert_dict)
            else:
                insert_dict["id"] = v_id
                mv.update_info(insert_dict)
            # --------------- 返回 -----------------
            return JsonResponse(code.con)
        except Exception:
            err = traceback.format_exc()
            moblog.warning(err)


# 人员
class monitorView(View):
    @classmethod
    def get(cls, request):
        """
        根据phoneid 获取手机所在台站的所属区域（台站）,返回这个区域(台站)下的监测人员信息名单
        :param request:
        :return:
        """
        try:
            # ------------------ 接收 -------------------
            ret = request.GET.dict()
            mobile = ret.get("phoneid")
            relog.info("getmonitor " + str(ret))
            # ----------------- 验证 --------------------
            if mobile is None:
                mobile = f.UNKNOW_MOBILE
            mobile_result = re.fullmatch(f.PHONEID_FORMATTER_RE, mobile)
            if mobile_result is None:
                mobile = f.UNKNOW_MOBILE
            # ---------------- 处理 ---------------------
            # ******* 序列化器 ************
            mob = serMobile()
            mon = serMonitor()
            # ******** 查询设备所属区域 ***********
            # 设备是否存在
            try:
                mob_obj = mob.table.get(mobile=mobile)
            except mob.table.model.DoesNotExist:
                mob_obj = mob.table.get(mobile=f.UNKNOW_MOBILE)
            # 设备是否删除
            if mob_obj.is_delete is 1:
                mobile = f.UNKNOW_MOBILE
            # ************** 查询该区域下的监测人员名单 ******************
            mon_list = mon.get_by_mobile(mobile)
            # ---------------- 返回 ----------------------
            con = code.con
            con["data"] = mon_list
            con["count"] = len(mon_list)
            return JsonResponse(con)
        except Exception:
            traceback.print_exc()


# 打卡
class userecordView(View):

    @classmethod
    def post(cls, request):
        try:
            # --------------- 接收 -------------------
            ret = request.body.decode()
            if ret is "":
                ret = {
                    "time": "",
                    "location": "",
                    "phoneid": "",
                    "idcard": "",
                    "version": "1.0.0"
                }
            else:
                ret = eval(ret)
            relog.info("userecord " + str(ret))
            time = ret.get("time")
            mobile = ret.get("phoneid")
            idcard = ret.get("idcard")
            version = ret.get("version")
            # ---------------- 验证 ----------------------
            time_result = re.fullmatch(f.DATE_FORMATTER_RE_PHONE, time)
            mobile_result = re.fullmatch(f.PHONEID_FORMATTER_RE, mobile)
            # idcard_result = re.fullmatch(f.IDCARD_FORMATTER_RE, idcard)
            # ---------------- 处理 ----------------------
            # ********* 格式转化器 *********
            tf = time_formatter()
            # ********** 序列化器 *************
            ur = serUserRecord()
            # ********* 错误格式处理 **********
            if time_result is None:
                time = tf.now_time_str
            else:
                time = tf.get_time_str(time)
            if mobile_result is None:
                mobile = f.UNKNOW_MOBILE
            # if idcard_result is None:
            #     idcard = f.UNKNOW_IDCARD
            # ------------ 格式转化 --------------------
            try:
                mob_obj = ur.mob.get(mobile=mobile)
            except ur.mob.model.DoesNotExist:
                mob_obj = ur.mob.get(mobile=f.UNKNOW_MOBILE)
            try:
                mon_obj = ur.mon.get(idcard=str(idcard))
            except ur.mon.model.DoesNotExist:
                mon_obj = ur.mon.get(idcard=f.UNKNOW_IDCARD)
            # ************ 组织数据插入数据库 **************
            insert_dict = dict()
            insert_dict["time"] = time
            insert_dict["mobile"] = mob_obj
            insert_dict["monitor"] = mon_obj
            insert_dict["version"] = version
            ur.insert_info(**insert_dict)
            # ---------------- 返回 ----------------------
            con = code.con
            return JsonResponse(con)
        except Exception:
            e = traceback.format_exc()
            errlog.warning(e)

# 白名单
class whitelistView(View):
    @classmethod
    def get(cls, request):
        """
        获取白名单
        :param request:
        :return:
        """
        try:
            # ---------- 接收 ---------------
            ret = request.GET.dict()
            relog.info("getwhitelist " + str(ret))
            mobile = ret.get("phoneid")
            # ----------- 验证 --------------
            if mobile is None:
                mobile = f.UNKNOW_MOBILE
            mobile_result = re.fullmatch(f.PHONEID_FORMATTER_RE, mobile)
            # ---------- 处理 ---------------
            if mobile_result is None:
                mobile = f.UNKNOW_MOBILE
            # --------- 序列化器 ------------
            wh = serWhiteList()
            # ------- redis操作 ------------
            whdis = whdisOp()
            # ------- 查询白名单 -----------
            # try:
            #     wh.mob.get(mobile=mobile)
            # except wh.mob.model.DoesNotExist:
            #     mobile = f.UNKNOW_MOBILE
            # --------- 记录地区 -----------
            dis_id = whdis.kv_get(mobile)
            if dis_id is None:
                content = wh.get_info_for_mobile(mobile)
            else:
                content = wh.get_info_by_district(dis_id)
            # ----------- 返回 --------------
            con = code.con
            con["data"] = content
            con["count"] = len(content)
            fr = formatterReturn()
            con = fr.get_whitelist(con)
            return JsonResponse(con)
        except Exception:
            e = traceback.format_exc()
            errlog.warning(e)

    @classmethod
    def post(cls, request):
        """
        编辑白名单,此处上传的白名单保存为手机所属台站的所属区域，类型不能为普通类型，上传普通类型一律改为区域类型
        :param request:
        :return:
        """
        try:
            # -------------- 接收 ----------------------
            ret = request.body.decode()
            if ret is "":
                ret = {
                    "time": "",
                    "freq": "",
                    "name": "",
                    "phoneid": "",
                    "type": "",
                    "district": ""
                }
            else:
                ret = eval(ret)
            relog.info("postwhitelist " + str(ret))
            # ----------------- 取数据 -------------------------
            time = ret.get("time")
            freq = ret.get("freq")
            name = ret.get("name")
            mobile = ret.get("phoneid")
            freq_type = ret.get("type")
            district = ret.get("district")
            # *********** 序列化器 ******************
            wc = serWhiteCategory()
            wh = serWhiteList()
            # --------------- 验证 ---------------------
            # *********** 验证 ***************
            time_result = re.fullmatch(f.DATE_FORMATTER_RE_PHONE, time)
            mobile_result = re.fullmatch(f.PHONEID_FORMATTER_RE, mobile)
            freq_result = re.fullmatch(f.INT_OR_FLOAT, str(freq))
            type_result = wc.is_type_legal(freq_type)
            # ---------------- 处理 -----------------------
            # *********** 格式转化器 ****************
            tf = time_formatter()
            ff = freq_formatter()
            # ********** 格式处理 *************
            if time_result is None:
                time = tf.now_time_str
            else:
                time = tf.get_time_str(time)
            if mobile_result is None:
                mobile = f.UNKNOW_MOBILE
            if freq_result is None:
                freq = f.UNKNOW_WHITELIST
            else:
                freq = ff.mobile_to_django(freq)
                if ff.isFreqLegal(freq) is False:
                    freq = f.UNKNOW_WHITELIST
            if not type_result:
                freq_type = f.UNKNOW_WHITECATEGORY
            # ********** 获取当前所属区 ************
            whdis = whdisOp()
            now_dis = whdis.kv_get(mobile)
            # 查找该频点
            vt = ViewTool()
            is_there, wh_obj = vt.getFreq_from_wh(now_dis, freq)
            # *********** 如果是删除白名单 *********
            if district is None:
                if is_there:
                    wh_obj.delete()
                else:
                    errlog.warning("白名单中无该频点，无法删除: ", freq)
                    con = code.con_false
                    con["msg"] = "白名单中无该频点"
                    return JsonResponse(con)
                con = code.con
                con["msg"] = "删除成功"
                return JsonResponse(con)
            else:
                # *********** 如果是编辑白名单 *************
                # 数据组织
                insert_dict = dict()
                insert_dict["time"] = time
                insert_dict["freq"] = freq
                if str(freq_type) == "4":  # 未知频点改为黑名单
                    freq_type = "5"
                insert_dict["type"] = freq_type
                insert_dict["district"] = now_dis
                insert_dict["name"] = name
                # 一级地区编号
                sys_dis = wh.dis.get(adcode=code.SYS_DISTRICT, is_district=1).id
                # 修改或加入该频点
                # ************* 如果是普通频点 ****************
                if str(freq_type) == "1":
                    insert_dict["district"] = sys_dis
                    # 检查该频点是否重复,重复则删除其他频点
                    if wh.table.filter(freq=freq).count() > 0:
                        wh.table.filter(freq=freq).delete()
                        wh.insert_info(insert_dict)
                    else:
                        wh.insert_info(insert_dict)

                # ************* 非普通频点 ****************
                else:
                    if is_there:
                        # 如果找到了该频点
                        wh_id = wh_obj.id
                        insert_dict["id"] = wh_id
                        # 修改
                        result = wh.update_info(insert_dict)
                        relog.info(result)
                    else:
                        # 未找到则插入
                        wh.insert_info(insert_dict)
            con = code.con
            return JsonResponse(con)
        except Exception:
            err = traceback.format_exc()
            moblog.warning(err)


# 地区#
class districtView(View):
    @classmethod
    def get(cls, request):
        """
        获取地区名单
        :param request:
        :return:
        """
        try:
            # ------------------ 接收 -----------------
            ret = request.GET.dict()
            mobile = ret.get("phoneid")
            relog.info("getdistrict " + str(ret))
            # ------------------ 验证 -----------------
            # ********* 序列化器 ***********
            dis = serDistrict()
            # ******************************
            if mobile is None:
                return JsonResponse(code.con_false)
            try:
                dis.mob.get(mobile=mobile)
            except dis.mob.model.DoesNotExist:
                return JsonResponse(code.con_false)
            # ------------------- 处理 ----------------
            # ********* 行政区名单 ************
            content = dis.get_city_list()
            # ********* 结果 ***************
            con = code.con
            con["data"] = content
            con["count"] = len(content)
            # ------------------- 返回 -----------------
            return JsonResponse(con)
        except Exception:
            e = traceback.format_exc()
            errlog.warning(e)

    @classmethod
    def post(cls, request):
        """
        根据地区获取白名单
        :param request:
        :return:
        """
        try:
            # ------------------ 接收 -----------------
            ret = request.body.decode()

            if ret is "":
                ret = {
                    "phoneid": "",
                    "district": ""
                }
            else:
                ret = eval(ret)
            relog.info("getdiswhitelist " + str(ret))
            mobile = ret.get("phoneid")
            district = ret.get("district")
            # ------------------ 验证 -----------------
            # ********* 序列化器 *************
            wh = serWhiteList()
            # ********************************
            # dis_result = re.fullmatch(f.INT_FORMATTER_RE, str(district))
            # mobile_result = re.fullmatch(f.PHONEID_FORMATTER_RE, mobile)
            # if dis_result is None:
            #     return JsonResponse(code.con_false)
            # if mobile_result is None:
            #     return JsonResponse(code.con_false)
            # try:
            #     wh.mob.get(mobile=mobile)
            # except wh.mob.model.DoesNotExist:
            #     return JsonResponse(code.con_false)
            # ------------------- 处理 ----------------
            # ------- redis操作类 ---------
            whdis = whdisOp()
            # ------ 记录地区 ------------
            whdis.kv_set(mobile, district)
            content = wh.get_info_by_district(district)
            con = code.con
            con["data"] = content
            con["count"] = len(content)
            # ------------------- 返回 -----------------
            return JsonResponse(con)
        except Exception:
            e = traceback.format_exc()
            errlog.warning(e)


class districtInfoView(View):
    @classmethod
    def get(cls, request):
        """
        获取手机所在地区
        :param request:
        :return:
        """
        try:
            # ----------- 接收 ---------------
            ret = request.GET.dict()
            relog.info("get-mobile-dis " + str(ret))
            mobile = ret.get("phoneid")
            # ----------- 验证 ---------------
            # ----------- 处理 ---------------
            # ********* 序列化器 *********
            dis = serDistrict()
            # 先判断redis 中是否有区域id信息
            whdis = whdisOp()
            dis_id = whdis.kv_get(mobile)
            if dis_id is None:
                # ********* 查找信息 *********
                result = dis.get_district_by_mobile(mobile)
            else:
                result = {
                    "district": dis_id,
                    "name": ""
                }
            # ----------- 返回 ---------------
            con = code.con
            con["data"] = result
            return JsonResponse(con)
        except Exception:
            e = traceback.format_exc()
            errlog.warning(e)

# 上传黑广播
class broadView(View):

    @classmethod
    def post(cls, request):
        """
        上传黑广播
        :param request:
        :return:
        """
        try:
            # ------------------ 接收 -----------------
            ret = request.body.decode()
            ret = eval(ret)
            mobile = str(ret.get("phoneid"))
            info_list = ret.get("data")
            # ------------------ 验证 -----------------
            # ******** 序列化器 ************
            br = serBlackRecord()
            # ********* 验证手机id **************
            try:
                br.mob.get(mobile=mobile)
            except br.mob.model.DoesNotExist:
                return JsonResponse(code.con_false)
            # ------------------- 处理 ----------------
            # *************** 数据处理 *****************
            result = list(map(broadInfoTurn, info_list))
            # *************** 保存数据库 **************
            save_to_mysql.delay(result)
            # *************** push到redis队列 *********
            # ********* 白名单过滤 ************
            content = list()
            for con in result:
                islegal = con.get("islegal")
                if str(islegal) == "0":
                    content.append(con)
                else:
                    continue
            # ********* redis操作类 *********
            bro = broadcastOp()
            mass = massmarkOp()
            # ********* 海量点 ***********
            mass_content = list(map(mass.formmater_data, content))  # 3号仓库
            for con in mass_content:
                k, v = con
                if k == "x,x":
                    continue
                else:
                    mass.list_push(k, v)
            # ********* 轮播表 ***********
            scroll_content = list(map(bro.formatter_scroll_info, content))
            for con in scroll_content:
                bro.list_push("scroll_n", con)
            # ********* 热力图 ***********
            heatmap_content = list(map(bro.formatter_heatmap_info, content))
            for con in heatmap_content:
                if con["lng"] == "x":
                    continue
                else:
                    bro.list_push("heatmap_n", con)
            # ------------------- 返回 -----------------
            con = code.con
            return JsonResponse(con)
        except Exception:
            e = traceback.format_exc()
            errlog.warning(e)


# 心跳包
class heartbeatView(View):
    @classmethod
    def post(cls, request):
        """
        上传心跳包
        :param request:
        :return:
        """
        try:
            # ------------------- 接收 ---------------
            ret = request.body.decode()
            if ret is "":
                ret = {
                    "phoneid": "",
                    "time": "",
                    "location": ""
                }
            else:
                ret = eval(ret)
            print(ret)
            relog.info("post-heartbeat " + str(ret))
            # *********** 取数据 ***********
            mobile = ret.get("phoneid")
            time = ret.get("time")
            lnglat = ret.get("location")
            # ------------------ 验证 -----------------
            mob = serMobile()
            try:
                mob.table.get(mobile=mobile)
            except mob.table.model.DoesNotExist:
                con = code.con_false
                con["msg"] = "该手机不存在"
                return JsonResponse(con)
            mobile_result = re.fullmatch(f.PHONEID_FORMATTER_RE, mobile)
            time_result = re.fullmatch(f.DATE_FORMATTER_RE_PHONE, time)
            lnglat_result = re.fullmatch(f.LNGLAT_FORMATTER_RE_PHONE, lnglat)
            # ------------------- 处理 ----------------
            # ********** reids操作类 ***********
            iw = isworkingOp()
            # ********** 格式转换器 **********
            tf = time_formatter()
            lf = lnglat_formatter()
            # ********** 格式处理 ***********
            if mobile_result is None:
                mobile = f.UNKNOW_MOBILE
            if time_result is None:
                time = tf.now_time_str
            else:
                time = tf.get_time_str(time)
            if lnglat_result is None:
                lnglat = f.UNKNOW_LNGLAT
            else:
                lnglat = lf.get_lnglat(lnglat)
            # *********** 组织数据 **************
            info = dict()
            info["time"] = time
            info["mobile"] = mobile
            info["lnglat"] = lnglat
            k, v = iw.formatter_info(info)
            if k == "None":
                pass
            else:
                # ********* 插入redis ***************
                iw.list_push(k, v)
            # ------------------- 返回 -----------------
            return JsonResponse(code.con)
        except Exception:
            err = traceback.format_exc()
            moblog.warning(err)


# 录音文件
class RecordingView(View):
    @classmethod
    def post(cls, request):
        """
        保存录音文件
        :param request:
        :return:
        """
        try:
            # ************** 保存路径 **********************
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
            ogg_dir = base_dir + '/static/mp3'
            print(ogg_dir)
            # -------------- 接收 ------------------
            re = request.FILES.dict()
            # ------------- 验证 -------------------
            if len(re.keys()) is 0:
                recordLogger.warning("录音文件不存在")
                return JsonResponse(code.con_false)
            # ------------- 处理 -------------------
            for k, v in re.items():
                data = v
                recordLogger.info(data.name)
                try:
                    destination = open(os.path.join(ogg_dir, data.name), 'wb')
                    for chunk in data.chunks():
                        destination.write(chunk)
                    destination.close()
                except Exception:
                    recordLogger.warning("音频文件保存失败")
                    con = code.con_false
                    return JsonResponse(con)
            # ------------- 返回 -------------------
            con = {
                "errno": 10000,
                "errmsg": "success",
                'path': ogg_dir
            }
            return JsonResponse(con)
        except Exception:
            e = traceback.format_exc()
            errlog.warning(e)


# 电台收测
class RedioTestView(View):
    @classmethod
    def post(cls, request):
        """
        电台收测记录
        :param request:
        :return:
        """
        try:
            # ----------- 接收 -------------
            ret = request.body.decode()
            if ret == "":
                ret = {
                    "time": "",
                    "location": "",
                    "phoneid": "",
                    "idcard": ""
                }
            else:
                ret = eval(ret)
            relog.info("post-rediotest " + str(ret))
            time = ret.get("time")
            lnglat = ret.get("location")
            mobile = ret.get("phoneid")
            monitor = ret.get("idcard")
            # --------------- 验证 ----------------
            # --------------- 处理 ----------------
            # ******** 格式化器 ***********
            tf = time_formatter()
            lf = lnglat_formatter()
            # ******* 序列化器 ************
            rt = serRedioTest()
            # ******* 数据处理 *************
            time = tf.get_time_str(time)
            lnglat = lf.get_lnglat(lnglat)
            try:
                mobile = rt.mob.get(mobile=mobile).id
            except rt.mob.model.DoesNotExist:
                mobile = rt.mob.get(mobile=f.UNKNOW_MOBILE).id
            try:
                monitor = rt.mon.get(idcard=monitor).id
            except rt.mon.model.DoesNotExist:
                monitor = rt.mon.get(idcard=f.UNKNOW_IDCARD).id
            # ******* 组织数据 **********
            insert_dict = dict()
            insert_dict["time"] = time
            insert_dict["lnglat"] = lnglat
            insert_dict["mobile"] = mobile
            insert_dict["monitor"] = monitor
            result = rt.insert_info(**insert_dict)
            # --------------- 返回 ----------------
            con = code.con
            con["data"] = result
            return JsonResponse(con)
        except Exception:
            e = traceback.format_exc()
            errlog.warning(e)

class ApkVersionView(View):
    @classmethod
    def get(cls, request):
        """
        获取某台手机对应平台的最新app版本号和apk下载地址
        :param request:
        :return:
        """
        try:
            # -------------- 接收 ------------------
            ret = request.GET.dict()
            relog.info("get-apk-version " + str(ret))
            mobile = ret.get("phoneid")
            # -------------- 验证 ------------------
            # -------------- 处理 ------------------
            # 序列化器
            mp = serMobileToPlatform()
            pf = serPlatform()
            # 查询手机对应平台
            platform_id = mp.table.get(mobile=mobile).platform
            platform = pf.table.get(id=platform_id)
            # 组织数据
            info = dict()
            info["version"] = platform.app
            apk = "-".join(platform.app.split("."))
            info["url"] = "/a/20" + apk + ".apk"
            # -------------- 返回 ------------------
            con = code.con
            con["data"] = info
            return JsonResponse(con)
        except Exception:
            e = traceback.format_exc()
            errlog.warning(e)


def broadInfoTurn(info):
    """
    广播信息处理
    :param info:
    :return:
    """
    try:
        # ********** 序列化器 **********
        bc = serBlackCategory()
        wh = serWhiteList()
        wc = serWhiteCategory()
        # ********** redis操作 ***********
        whdis = whdisOp()
        # ********** 格式化器 **********
        lf = lnglat_formatter()
        ff = freq_formatter()
        tf = time_formatter()
        # ********** 组织数据 **********
        con = dict()
        info["category"] = str(int(info["category"]) + 1)
        try:
            con["category"] = bc.table.get(id=info.get("category"))
        except bc.table.model.DoesNotExist:
            con["category"] = bc.table.get(id=f.UNKNOW_BLACKCATEGORY)
        try:
            con["mobile"] = bc.mob.get(mobile=info.get("phoneid"))
        except bc.mob.model.DoesNotExist:
            con["mobile"] = bc.mob.get(mobile=f.UNKNOW_MOBILE)
        con["lnglat"] = lf.get_lnglat(info.get("location"))
        con["freq"] = ff.mobile_to_django(info.get("freq"))
        con["time"] = tf.get_time_str(info.get("time"))
        con["record"] = info.get("record") + ".ogg"
        con["acquisitionmode"] = info.get("acquisitionmode")
        con["confidencelevel"] = info.get("confidencelevel")
        # ******** 备注与联系方式 ***********
        con["common"] = info.get("common")
        con["contact"] = info.get("contact")
        if con["common"] == None:
            con["common"] = ""
        if con["contact"] == None:
            con["contact"] = ""
        # ********** 获取地理相关信息 ***********
        if con.get("lnglat") == "x,x":
            con["address"] = ""
            con["adcode"] = f.UNKNOW_ADCODE
        else:
            address_info = t.getaddress(con.get("lnglat"))
            con["address"] = address_info["formatted_address"]
            con["adcode"] = address_info["adcode"]
        # ********** 白名单过滤 ***************
        freq = con.get("freq")
        mobile = con.get("mobile").mobile
        dis_id = whdis.kv_get(mobile)
        # tg_dis = con.get("mobile").district
        # dis_id = wh.dis.get(id=tg_dis).superior
        wh_list = wh.get_info_by_district(dis_id)
        con["islegal"] = 0
        for wh_info in wh_list:
            if str(freq) == str(wh_info.get("freq")):
                wh_type = wh_info.get("type")
                try:
                    con["islegal"] = wc.table.get(id=wh_type).islegal
                except wc.table.model.DoesNotExist:
                    con["islegal"] = 0
        return con
    except Exception:
        e = traceback.format_exc()
        errlog.warning(e)

class ViewTool:
    def __init__(self):
        self.wh = serWhiteList()

    def getFreq_from_wh(self, district, freq):
        """
        在白名单中查询某个频点（范围是该地区白名单与普通白名单）
        :param district: 地区
        :param freq:
        :return:
        """
        # 查询集
        query = self.wh.get_query_by_district(district)
        is_There = True
        try:
            wh_obj = query.get(freq=freq)
        except self.wh.table.model.DoesNotExist:
            is_There = False
            wh_obj = None
        return (is_There, wh_obj)
