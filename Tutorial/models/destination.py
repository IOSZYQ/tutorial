__author__ = "HanHui"

from django.db import models


class Destination(models.Model):
    source         = models.CharField(max_length=32)
    sourceId       = models.CharField(max_length=32, null=True)
    countryCode    = models.CharField(max_length=16, null=True)
    version        = models.CharField(max_length=64, null=True)
    tosId          = models.IntegerField(null=True)
    longitude      = models.FloatField(null=True)
    latitude       = models.FloatField(null=True)
    name_cn        = models.CharField(max_length=255, null=True)
    name_en        = models.CharField(max_length=255, null=True)
    inactive       = models.BooleanField(default=False)
    created        = models.DateTimeField(auto_now_add=True)
    updated        = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "Tutorial"

        index_together = [
            ["inactive", "tosId"]
        ]


class DestinationUpdate(models.Model):
    source          = models.CharField(max_length=32)
    sourceId        = models.CharField(max_length=32, null=True)
    countryCode     = models.CharField(max_length=16, null=True)
    subCities       = models.TextField(null=True)
    longitude       = models.FloatField(null=True)
    latitude        = models.FloatField(null=True)
    json            = models.TextField()
    created         = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "Tutorial"
