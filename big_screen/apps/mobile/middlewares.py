from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
import traceback
import logging

from big_screen.utils import sys_setting as code
from big_screen.redisOpration.AllOpration import MobListOp

errlog = logging.getLogger("Process")


class MD1(MiddlewareMixin):
    def process_request(self, request):
        try:
            path = request.path.split("/")
            re_type = path[2]
            if re_type == "phone":
                moblist_op = MobListOp()
                mob_list = moblist_op.get_mob_list()
                re_method = request.method
                if re_method == "GET":
                    ret = request.GET.dict()
                    mobile = ret.get("phoneid")
                    if mobile not in mob_list:
                        errlog.warning(mobile)
                        con = code.con_false
                        return JsonResponse(con)
                if re_method == "POST" and path[3] != "record":
                    ret = request.body.decode()
                    ret = eval(ret)
                    mobile = ret.get("phoneid")
                    if mobile not in mob_list:
                        errlog.warning(mobile)
                        con = code.con_false
                        return JsonResponse(con)
        except Exception:
            e = traceback.format_exc()
            errlog.warning(e)
