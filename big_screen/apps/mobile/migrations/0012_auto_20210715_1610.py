# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-07-15 16:10
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobile', '0011_auto_20210715_1607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobileversion',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 15, 16, 10, 59, 34062), verbose_name='更新时间'),
        ),
        migrations.AlterField(
            model_name='rediotest',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 15, 16, 10, 59, 34062), verbose_name='收测时间'),
        ),
    ]
