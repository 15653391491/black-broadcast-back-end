# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-07-05 11:32
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whiteList', '0004_auto_20210621_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='whitelist',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 5, 11, 32, 42, 889889), verbose_name='加入时间'),
        ),
    ]
