# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-07-15 16:07
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whiteList', '0011_auto_20210705_1205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='whitelist',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 15, 16, 7, 17, 290554), verbose_name='加入时间'),
        ),
    ]