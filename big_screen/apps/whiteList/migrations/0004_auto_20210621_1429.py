# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-06-21 14:29
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whiteList', '0003_auto_20210309_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='whitelist',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 6, 21, 14, 29, 51, 321306), verbose_name='加入时间'),
        ),
    ]
