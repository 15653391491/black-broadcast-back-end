# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-14 09:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('con_control', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitorinfo',
            name='district',
            field=models.IntegerField(default=110000, verbose_name='所属区域'),
        ),
    ]
