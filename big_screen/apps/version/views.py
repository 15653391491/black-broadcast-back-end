from django.views import View
from django.http.response import JsonResponse
import traceback

from big_screen.utils import sys_setting as code
from big_screen.serialization.allSerialization import serMobileToPlatform, serPlatform


# Create your views here.

class GetAppVersion(View):
    @classmethod
    def get(cls, request):
        """
        获取某台手机对应平台的最新app版本号和apk下载地址
        :param request:
        :return:
        """
        print('111')
        try:
            # -------------- 接收 ------------------
            ret = request.GET.dict()
            mobile = ret.get("mobile")
            # -------------- 验证 ------------------
            # -------------- 处理 ------------------
            # 序列化器
            mp = serMobileToPlatform()
            pf = serPlatform()
            # 查询手机对应平台
            platform_id = mp.table.get(mobile=mobile)
            platform = pf.table.get(id=platform_id)
            # -------------- 返回 ------------------
            con = code.con
            con['data'] = platform
            print(con)
            return JsonResponse(con)
        except Exception:
            e = traceback.format_exc()
            print(e)
