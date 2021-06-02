from django.db import models


# Create your models here.
class MobileToPlatformInfo(models.Model):
    name =models.CharField(max_length=50,verbose_name="手机名",default="none")
    mobile = models.CharField(max_length=50, verbose_name="手机id")
    platform = models.IntegerField(default=0, verbose_name="平台")

    class Meta:
        db_table = "tb_MobileToPlatform"
        verbose_name = "手机对应平台"


class PlatformInfo(models.Model):
    version = models.CharField(max_length=50, verbose_name="平台版本")
    district = models.CharField(max_length=50, verbose_name="平台所属地区")
    app = models.CharField(max_length=50, verbose_name="app版本号")

    class Meta:
        db_table = "tb_Platform"
        verbose_name = "平台信息"
