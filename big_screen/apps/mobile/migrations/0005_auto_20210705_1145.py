# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-07-05 11:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobile', '0004_auto_20210705_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobileversion',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 5, 11, 45, 1, 586783), verbose_name='更新时间'),
        ),
        migrations.AlterField(
            model_name='rediotest',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 5, 11, 45, 1, 586783), verbose_name='收测时间'),
        ),
    ]
