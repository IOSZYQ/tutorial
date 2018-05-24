# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-24 10:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Destination',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=32)),
                ('sourceId', models.CharField(max_length=32, null=True)),
                ('version', models.CharField(max_length=64, null=True)),
                ('tosId', models.IntegerField(null=True)),
                ('countryCode', models.CharField(max_length=16, null=True)),
                ('adminLevel', models.IntegerField()),
                ('parentId', models.CharField(max_length=32, null=True)),
                ('name_cn', models.CharField(max_length=255, null=True)),
                ('name_en', models.CharField(max_length=255, null=True)),
                ('longitude', models.FloatField(null=True)),
                ('latitude', models.FloatField(null=True)),
                ('inactive', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='DestinationUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=32)),
                ('sourceId', models.CharField(max_length=32, null=True)),
                ('countryCode', models.CharField(max_length=16, null=True)),
                ('json', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Dida',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('countryFile', models.FilePathField(null=True)),
                ('cityFile', models.FilePathField(null=True)),
                ('hotelFile', models.FilePathField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('normalizeTime', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=32)),
                ('sourceId', models.IntegerField(unique=True)),
                ('version', models.CharField(max_length=64, null=True)),
                ('tosId', models.IntegerField(null=True)),
                ('cityId', models.CharField(max_length=32)),
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
                ('public', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='HotelUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=32)),
                ('sourceId', models.IntegerField(unique=True)),
                ('json', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterIndexTogether(
            name='destination',
            index_together=set([('inactive', 'tosId')]),
        ),
    ]
