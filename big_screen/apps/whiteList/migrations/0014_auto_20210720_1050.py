# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-07-20 10:50
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whiteList', '0013_auto_20210715_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='whitelist',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 20, 10, 50, 6, 373873), verbose_name='加入时间'),
        ),
    ]
