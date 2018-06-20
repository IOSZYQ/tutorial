__author__ = "HanHui"

from django.db import models


class Destination(models.Model):
    source         = models.CharField(max_length=32)
    sourceId       = models.CharField(max_length=32)
    version        = models.CharField(max_length=64, null=True)
    tosId          = models.IntegerField(null=True, db_index=True)
    longitude      = models.FloatField(null=True)
    latitude       = models.FloatField(null=True)
    latitudeN      = models.FloatField(null=True)
    latitudeS      = models.FloatField(null=True)
    longitudeE     = models.FloatField(null=True)
    longitudeW     = models.FloatField(null=True)
    adminLevel     = models.IntegerField(default=1)
    name_cn        = models.CharField(max_length=255, null=True)
    name_en        = models.CharField(max_length=255, null=True)
    inactive       = models.BooleanField(default=False)
    created        = models.DateTimeField(auto_now_add=True)
    updated        = models.DateTimeField(auto_now=True)
    parent         = models.ForeignKey("self", null=True, related_name="children")

    class Meta:
        app_label = "Tutorial"

        unique_together = [
            ("source", "sourceId")
        ]


class DestinationSubCity(models.Model):
    cityId = models.CharField(max_length=32)
    destination = models.ForeignKey(Destination, related_name="subCities")

    class Meta:
        app_label = "Tutorial"


class DestinationUpdate(models.Model):
    json            = models.TextField()
    created         = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)
    destination     = models.OneToOneField(Destination, related_name="update")

    class Meta:
        app_label = "Tutorial"
