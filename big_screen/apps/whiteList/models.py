from django.db import models
import datetime
default_time = datetime.datetime.now()

class WhiteList(models.Model):
    time = models.DateTimeField(default=default_time,verbose_name='加入时间')
    name = models.CharField(default='none', max_length=50, verbose_name='频道名称')
    freq = models.FloatField(verbose_name='频点')
    district = models.IntegerField(default=1, verbose_name="所属区域")
    type = models.IntegerField(default=1, verbose_name="种类")

    class Meta:
        db_table = 'tb_whitelist'
        verbose_name = '白名单'


class WhiteListCategory(models.Model):
    name = models.CharField(default="普通", max_length=50, verbose_name="类型名称")
    islegal = models.CharField(max_length=50, default="1", verbose_name="是否合法")

    class Meta:
        db_table = "tb_whcategory"
        verbose_name = "白名单类型"
