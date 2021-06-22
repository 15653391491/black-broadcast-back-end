from django.db import models
import datetime
default_time = datetime.datetime.now()

# Create your models here.
class MobileVersion(models.Model):
    time = models.DateTimeField(default=default_time,verbose_name="更新时间")
    mobile = models.IntegerField(default=0, verbose_name="设备")
    version = models.CharField(max_length=50, default="1.0.0", verbose_name="版本")

    class Meta:
        db_table = 'tb_version'
        verbose_name = "当前设备版本"


class RedioTest(models.Model):
    time = models.DateTimeField(default=default_time,verbose_name="收测时间")
    mobile = models.IntegerField(default=0, verbose_name="收测设备")
    monitor = models.IntegerField(default=0, verbose_name="收测人")
    lnglat = models.CharField(max_length=50, default="x,x", verbose_name="收测坐标")

    class Meta:
        db_table = "tb_rediotest"
        verbose_name = "收测记录"
