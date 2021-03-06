# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-09 20:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='行政区名')),
                ('superior', models.IntegerField(default=0, verbose_name='上级行政区')),
                ('adcode', models.IntegerField(default=0, verbose_name='行政区编码')),
                ('is_district', models.IntegerField(default=1, verbose_name='是否为行政区')),
            ],
            options={
                'verbose_name': '行政区',
                'db_table': 'tb_district',
            },
        ),
        migrations.CreateModel(
            name='MobileInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='none', max_length=50, verbose_name='名称')),
                ('time', models.DateTimeField(verbose_name='加入时间')),
                ('mobile', models.CharField(max_length=50, unique=True, verbose_name='系统编号')),
                ('phonenumber', models.CharField(default='00000000000', max_length=50, verbose_name='电话号码')),
                ('is_delete', models.BooleanField(default=0, verbose_name='是否已经删除')),
                ('district', models.IntegerField(verbose_name='所属区域')),
            ],
            options={
                'verbose_name': '移动端信息',
                'db_table': 'tb_MobileInfo',
            },
        ),
        migrations.CreateModel(
            name='MobileNewLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(verbose_name='当前日期时间')),
                ('lnglat', models.CharField(max_length=50, verbose_name='当前位置')),
                ('mobile', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='con_control.MobileInfo', verbose_name='移动端信息')),
            ],
            options={
                'verbose_name': '新的当前检测人员位置',
                'db_table': 'tb_location',
            },
        ),
        migrations.CreateModel(
            name='MobileUseRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(verbose_name='时间')),
                ('mobile', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='con_control.MobileInfo', verbose_name='手机')),
            ],
            options={
                'verbose_name': '手机使用记录',
                'db_table': 'tb_mobileuserecord',
            },
        ),
        migrations.CreateModel(
            name='MonitorInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(verbose_name='加入时间')),
                ('idcard', models.CharField(max_length=50, unique=True, verbose_name='身份证')),
                ('name', models.CharField(max_length=50, verbose_name='姓名')),
                ('district', models.IntegerField(default=520000, verbose_name='所属区域')),
                ('is_delete', models.IntegerField(default=0, verbose_name='是否已经删除')),
            ],
            options={
                'verbose_name': '监测人员信息',
                'db_table': 'tb_MonitorInfo',
            },
        ),
        migrations.AddField(
            model_name='mobileuserecord',
            name='monitor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='con_control.MonitorInfo', verbose_name='使用人员'),
        ),
    ]
