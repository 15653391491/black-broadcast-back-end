# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-07-05 12:05
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobile', '0009_auto_20210705_1158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobileversion',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 5, 12, 5, 27, 698850), verbose_name='更新时间'),
        ),
        migrations.AlterField(
            model_name='rediotest',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 5, 12, 5, 27, 698850), verbose_name='收测时间'),
        ),
    ]
