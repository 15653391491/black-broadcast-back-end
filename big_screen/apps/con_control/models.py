from django.db import models

from big_screen.utils import sys_setting as code
import datetime
default_time = datetime.datetime.now()

# Create your models here.


class MonitorInfo(models.Model):
    time = models.DateTimeField(default=default_time,verbose_name='加入时间')
    idcard = models.CharField(unique=True, max_length=50, verbose_name='身份证')
    name = models.CharField(max_length=50, verbose_name='姓名')
    district = models.IntegerField(default=code.SYS_DISTRICT, verbose_name="所属区域")
    is_delete = models.IntegerField(default=0, verbose_name="是否已经删除")

    class Meta:
        db_table = 'tb_MonitorInfo'
        verbose_name = '监测人员信息'


class MobileInfo(models.Model):
    name = models.CharField(default="none", max_length=50, verbose_name='名称')
    time = models.DateTimeField(default=default_time,verbose_name='加入时间')
    mobile = models.CharField(unique=True, max_length=50, verbose_name='系统编号')
    phonenumber = models.CharField(default="0" * 11, max_length=50, verbose_name='电话号码')
    is_delete = models.BooleanField(default=0, verbose_name='是否已经删除')
    district = models.IntegerField(verbose_name="所属区域")

    class Meta:
        db_table = 'tb_MobileInfo'
        verbose_name = '移动端信息'


class MobileNewLocation(models.Model):
    time = models.DateTimeField(default=default_time,verbose_name='当前日期时间')
    mobile = models.ForeignKey(
        MobileInfo, verbose_name='移动端信息', on_delete=models.DO_NOTHING)
    lnglat = models.CharField(max_length=50, verbose_name='当前位置')

    class Meta:
        db_table = 'tb_location'
        verbose_name = '新的当前检测人员位置'


class District(models.Model):
    name = models.CharField(max_length=50, verbose_name="行政区名")
    superior = models.IntegerField(default=0, verbose_name="上级行政区")
    adcode = models.IntegerField(default=0, verbose_name="行政区编码")
    is_district = models.IntegerField(default=1, verbose_name="是否为行政区")

    # superior = models.ForeignKey(self, null=True)

    class Meta:
        db_table = 'tb_district'
        verbose_name = "行政区"


class MobileUseRecord(models.Model):
    time = models.DateTimeField(default=default_time,verbose_name="时间")
    monitor = models.ForeignKey(
        MonitorInfo, verbose_name="使用人员", on_delete=models.DO_NOTHING)
    mobile = models.ForeignKey(
        MobileInfo, verbose_name="手机", on_delete=models.DO_NOTHING)
    version = models.CharField(max_length=50, default='1.0.0', verbose_name='打卡时的版本')

    # usetype = models.BooleanField(default=True, verbose_name="种类")

    class Meta:
        db_table = "tb_mobileuserecord"
        verbose_name = "手机使用记录"
