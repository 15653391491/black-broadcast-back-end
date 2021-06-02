from django.db import models
from con_control.models import MobileInfo
import datetime

default_time = datetime.datetime.now()

class BlackCategory(models.Model):
    time = models.DateTimeField(default=default_time,verbose_name='加入时间')
    name = models.CharField(max_length=50, verbose_name='种类名称')
    num = models.CharField(default='0', max_length=50, verbose_name='编码')

    class Meta:
        db_table = 'tb_BlackCategory'
        verbose_name = '黑广播种类'


class BlackRecord(models.Model):
    time = models.DateTimeField(blank=False, verbose_name='上传时间')
    lnglat = models.CharField(max_length=50, blank=False, verbose_name='上传坐标')
    mobile = models.ForeignKey(MobileInfo, blank=False, verbose_name='上传手机系统id', on_delete=models.DO_NOTHING)
    address = models.CharField(max_length=100, default='null', verbose_name='坐标具体可读地址')
    datafrom = models.CharField(default="baidu", max_length=50, verbose_name="可读地址数据来源")
    district = models.IntegerField(default=1, verbose_name="所属区域")
    freq = models.FloatField(blank=False, verbose_name='频率')
    name = models.CharField(default='0', max_length=50, verbose_name='频点名称')
    category = models.ForeignKey(BlackCategory, verbose_name='种类', on_delete=models.DO_NOTHING)
    record = models.CharField(default='0', blank=False, max_length=100, verbose_name='录音名称')
    recordtime = models.CharField(default='0s', blank=False, max_length=50, verbose_name='录音时长')
    acquisitionmode = models.CharField(default='0', blank=False, max_length=50, verbose_name='采集模式')
    confidencelevel = models.CharField(default='0', blank=False, max_length=50, verbose_name='黑广播置信度')
    islegal = models.CharField(default='0', blank=False, max_length=50, verbose_name='是否合法')
    contact = models.CharField(default='无', blank=False, max_length=50, verbose_name='联系方式')
    common = models.CharField(default='无', blank=False, max_length=300, verbose_name='备注')

    class Meta:
        db_table = 'tb_Broadcasting'
        verbose_name = '黑广播记录'
