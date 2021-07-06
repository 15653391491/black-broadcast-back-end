# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-07-05 11:32
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('con_control', '0005_auto_20210621_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobileinfo',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 5, 11, 32, 42, 882935), verbose_name='加入时间'),
        ),
        migrations.AlterField(
            model_name='mobilenewlocation',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 5, 11, 32, 42, 882935), verbose_name='当前日期时间'),
        ),
        migrations.AlterField(
            model_name='mobileuserecord',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 5, 11, 32, 42, 882935), verbose_name='时间'),
        ),
        migrations.AlterField(
            model_name='monitorinfo',
            name='district',
            field=models.IntegerField(default=150300, verbose_name='所属区域'),
        ),
        migrations.AlterField(
            model_name='monitorinfo',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 5, 11, 32, 42, 882935), verbose_name='加入时间'),
        ),
    ]
