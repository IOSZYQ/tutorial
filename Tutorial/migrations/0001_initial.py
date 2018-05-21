# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-21 17:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DidaBedType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typeId', models.IntegerField(unique=True)),
                ('defaultOccupancy', models.IntegerField()),
                ('name_cn', models.CharField(default='', max_length=64)),
                ('name_en', models.CharField(default='', max_length=64)),
                ('inactive', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DidaBreakfastType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typeId', models.IntegerField(unique=True)),
                ('name_cn', models.CharField(default='', max_length=64)),
                ('name_en', models.CharField(default='', max_length=64)),
                ('inactive', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DidaCity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sourceId', models.CharField(max_length=32, unique=True)),
                ('parentId', models.CharField(max_length=32, null=True)),
                ('name_cn', models.CharField(max_length=255, null=True)),
                ('name_en', models.CharField(max_length=255, null=True)),
                ('longitude', models.FloatField(null=True)),
                ('latitude', models.FloatField(null=True)),
                ('destId', models.IntegerField(null=True)),
                ('inactive', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DidaCountry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sourceId', models.CharField(max_length=32, unique=True)),
                ('name_cn', models.CharField(max_length=255, null=True)),
                ('name_en', models.CharField(max_length=255, null=True)),
                ('destId', models.IntegerField(null=True)),
                ('longitude', models.FloatField(null=True)),
                ('latitude', models.FloatField(null=True)),
                ('inactive', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DidaHotel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sourceId', models.IntegerField(unique=True)),
                ('name_en', models.CharField(max_length=128)),
                ('name_cn', models.CharField(max_length=128)),
                ('address', models.CharField(max_length=1024, null=True)),
                ('zipCode', models.CharField(max_length=32, null=True)),
                ('latitude', models.FloatField(null=True)),
                ('longitude', models.FloatField(null=True)),
                ('geohash8', models.CharField(db_index=True, max_length=16)),
                ('starRating', models.CharField(max_length=32)),
                ('telephone', models.CharField(max_length=128, null=True)),
                ('amenity', models.TextField(null=True)),
                ('rooms', models.TextField(null=True)),
                ('inactive', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('poiId', models.IntegerField(null=True)),
                ('public', models.BooleanField(default=False)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hotels', to='Tutorial.DidaCity')),
            ],
        ),
        migrations.AlterIndexTogether(
            name='didacountry',
            index_together=set([('inactive', 'destId')]),
        ),
        migrations.AddField(
            model_name='didacity',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cities', to='Tutorial.DidaCountry'),
        ),
        migrations.AlterIndexTogether(
            name='didacity',
            index_together=set([('inactive', 'destId')]),
        ),
    ]
