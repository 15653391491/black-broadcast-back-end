# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-03-09 15:25
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobile', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobileversion',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 9, 15, 25, 6, 779076), verbose_name='更新时间'),
        ),
        migrations.AlterField(
            model_name='mobileversion',
            name='version',
            field=models.CharField(default='1.0.0', max_length=50, verbose_name='版本'),
        ),
        migrations.AlterField(
            model_name='rediotest',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 9, 15, 25, 6, 779076), verbose_name='收测时间'),
        ),
    ]
