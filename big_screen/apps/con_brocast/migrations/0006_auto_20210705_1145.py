# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-07-05 11:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('con_brocast', '0005_auto_20210705_1145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blackcategory',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 5, 11, 45, 39, 194710), verbose_name='加入时间'),
        ),
    ]
