from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging

errlog = logging.getLogger("Process")


# Create your views here.


def index(request):
    """
    判断是否已经登录
    :param request:
    :return:
    """
    if request.user.is_authenticated():
        return JsonResponse({'msg': '0'})
    else:
        errlog.info('err')
        return JsonResponse({'msg': '1'})


def loginview(request):
    """
    登录接口
    :param request:
    :return:
    """
    try:
        ret = eval(request.body.decode())
    except Exception as e:
        errlog.info(repr(e))
        ret = eval(request.POST.get('json'))
    print(ret)
    username = ret['username']
    password = ret['password']
    user = authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({'msg': '密码错误'})
    try:
        is_login = user.is_authenticated
    except Exception as e:
        errlog.info(repr(e))
        return JsonResponse({'msg': '密码错误'})
    if is_login:
        login(request, user)
        return JsonResponse({'msg': '0'})
    else:
        return JsonResponse({'msg': 'unlogin'})


def register(request):
    return render(request, 'register.html')


def logout(request):
    return redirect('index')


def isthererecord(request):
    return JsonResponse({'code': '0'})
