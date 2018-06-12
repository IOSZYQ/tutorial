__author__ = "HanHui"

from django.db import models


class Hotel(models.Model):
    source         = models.CharField(max_length=32)
    sourceId       = models.CharField(max_length=32)
    version        = models.CharField(max_length=64, null=True)
    tosId          = models.IntegerField(null=True)
    cityId         = models.CharField(max_length=32)
    name_en        = models.CharField(max_length=128)
    name_cn        = models.CharField(max_length=128)
    address        = models.CharField(max_length=1024, null=True)
    zipCode        = models.CharField(max_length=32, null=True)
    latitude       = models.FloatField(null=True)
    longitude      = models.FloatField(null=True)
    geohash8       = models.CharField(max_length=16, null=True)
    starRating     = models.CharField(max_length=32)
    telephone      = models.CharField(max_length=128, null=True)
    inactive       = models.BooleanField(default=False)
    created        = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "Tutorial"


class HotelUpdate(models.Model):
    source          = models.CharField(max_length=32)
    sourceId        = models.IntegerField(unique=True)
    cityId          = models.CharField(max_length=32, null=True)
    countryCode     = models.CharField(max_length=16, null=True)
    latitude        = models.FloatField(null=True)
    longitude       = models.FloatField(null=True)
    json            = models.TextField()
    created         = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "Tutorial"
        index_together = [
            ("source", "cityId")
        ]
