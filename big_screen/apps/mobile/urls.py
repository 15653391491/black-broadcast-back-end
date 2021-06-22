"""big_screen URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^d/phone/version', views.versionView.as_view()),
    url(r'^d/phone/district', views.districtView.as_view()),
    url(r'^d/phone/disinfo', views.districtInfoView.as_view()),
    url(r'^d/phone/whitelist', views.whitelistView.as_view()),
    url(r'^d/phone/userecord', views.userecordView.as_view()),
    url(r'^d/phone/broadcast', views.broadView.as_view()),
    url(r'^d/phone/isworking', views.heartbeatView.as_view()),
    url(r'^d/phone/monitor', views.monitorView.as_view()),
    url(r'^d/phone/record', views.RecordingView.as_view()),
    url(r'^d/phone/rediotest', views.RedioTestView.as_view()),
    url(r'^d/phone/apkversion$', views.ApkVersionView.as_view())
]
