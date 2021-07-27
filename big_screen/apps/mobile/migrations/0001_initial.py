# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-09 20:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MobileVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(verbose_name='更新时间')),
                ('mobile', models.IntegerField(default=0, verbose_name='设备')),
                ('version', models.CharField(default='', max_length=50, verbose_name='版本')),
            ],
            options={
                'verbose_name': '当前设备版本',
                'db_table': 'tb_version',
            },
        ),
        migrations.CreateModel(
            name='RedioTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(verbose_name='收测时间')),
                ('mobile', models.IntegerField(default=0, verbose_name='收测设备')),
                ('monitor', models.IntegerField(default=0, verbose_name='收测人')),
                ('lnglat', models.CharField(default='x,x', max_length=50, verbose_name='收测坐标')),
            ],
            options={
                'verbose_name': '收测记录',
                'db_table': 'tb_rediotest',
            },
        ),
    ]