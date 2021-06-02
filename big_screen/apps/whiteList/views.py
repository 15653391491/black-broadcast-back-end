from django.views import View
from django.http import JsonResponse
from django.core.paginator import Paginator
import logging

from big_screen.serialization.allSerialization import serWhiteList
from big_screen.utils import sys_setting as code
from big_screen.utils.box.formatter_return import formatterReturn

logger = logging.getLogger('Whitelist')
errlog = logging.getLogger("Process")
relog = logging.getLogger("request")
bodylog = logging.getLogger("body")


# √
class WhiteListTextView(View):
    # √
    @classmethod
    def get(cls, request):
        """
        页面获取白名单
        :param request:
        :return:
        """
        try:
            # --------------- 准备 --------------------
            # ********* 接收 ************
            ret = request.GET
            # ********* 序列化器 ********
            s = serWhiteList()
            is_mobile = False
            # ------------- 组织数据 ----------------
            if "phoneid" in ret.keys():
                mobile = ret.get("phoneid")
                limit = 15
                is_mobile = True
            else:
                mobile = "111111111111111"
                limit = ret.get("limit")
            page = ret.get("page")
            info_list = s.get_info(mobile)
            # --------------- 分页 -----------------
            paginator = Paginator(info_list, limit)
            content = list()
            for info in paginator.page(page):
                content.append(info)
            # --------------- 返回 ------------------
            con = {
                "data": content,
                "code": code.STATUSCODE_SUCCESS,
                "msg": "success",
                "count": len(info_list)
            }
            f = formatterReturn()
            if is_mobile:
                con = f.get_whitelist(con)
            return JsonResponse(con)
        except Exception:
            traceback.print_exc()

    # √
    @classmethod
    def post(cls, request):
        """
        添加白名单
        :param request:
        :return:
        """
        # try:
        # ------------- 接收 ------------------
        ret = eval(request.body.decode())
        # ------------- 序列化器 --------------
        s = serWhiteList()
        # ------------- 处理 ------------------
        mobile = ret.pop("phoneid")
        con = s.insert_info(mobile, ret)
        return JsonResponse(con)
        # except Exception:
        # traceback.print_exc()

    # √
    @classmethod
    def delete(cls, request):
        ret = eval(request.body.decode())
        s = serWhiteList()
        # ret["id"] = s.table.get(freq=ret.pop("freq"), district=ret.pop("district")).id
        con = s.delete_info(ret)
        # con = code.con
        return JsonResponse(con)

    # √
    @classmethod
    def patch(cls, request):
        """
        修改白名单的区域和名称
        :param request:
        :return:
        """
        # ------------- 接收 -----------------
        ret = eval(request.body.decode())
        # ------------- 序列化器 -----------------
        s = serWhiteList()
        # ------------- 查询 ----------------
        # ret["id"] = s.table.get(freq=ret.pop("freq"), district=ret.pop("district")).id
        # ------------- 修改 --------------
        con = s.update_info(ret)
        # -------------- 返回 -------------
        return JsonResponse(con)
