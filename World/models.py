__author__ = 'swolfod'


from django.db import models


class Destination(models.Model):
    name = models.CharField(max_length=128, db_index=True)
    name_cn = models.CharField(max_length=32, default="", db_index=True)
    name_en = models.CharField(max_length=128, default="", db_index=True)
    pic = models.CharField(max_length=256, null=True)
    description = models.TextField(null=True)

    adminLevel = models.IntegerField(db_index=True)

    ISO = models.CharField(max_length=16)
    ISO2 = models.CharField(max_length=16)
    sovereignty = models.CharField(max_length=256, null=True)
    formalName = models.CharField(max_length=256, null=True)
    alternativeNames = models.CharField(max_length=256, null=True)

    latitude = models.FloatField()
    longitude = models.FloatField()
    latitudeN = models.FloatField()
    latitudeS = models.FloatField()
    longitudeE = models.FloatField()
    longitudeW = models.FloatField()

    shapeN = models.FloatField()
    shapeS = models.FloatField()
    shapeE = models.FloatField()
    shapeW = models.FloatField()

    parent = models.ForeignKey("self", null=True, related_name="children")
    creatorId = models.IntegerField(null=True)
    inactive = models.BooleanField(default=False)
    public = models.BooleanField(default=True)
    weight = models.IntegerField(default=0)
    timeStamp = models.BigIntegerField(null=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        app_label = "World"

        index_together = [
            ["parent", "adminLevel", "weight"],
            ["timeStamp", "id"],
            ["creatorId", "inactive"]
        ]


class DestinationShape(models.Model):
    destination = models.ForeignKey(Destination, related_name="shapePoints")
    index = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        app_label = "World"

        index_together = [
            ["destination", "index"],
        ]


class DestinationAlias(models.Model):
    destination = models.ForeignKey(Destination, related_name="aliases")
    alias = models.CharField(max_length=128)

    class Meta:
        app_label = "World"


class DestinationInfo(models.Model):
    destination = models.ForeignKey(Destination, related_name="infos")
    infoTitle = models.CharField(max_length=1024)
    infoContent = models.TextField()

    class Meta:
        app_label = "World"


class DestinationCard(models.Model):
    destination = models.ForeignKey(Destination, related_name="cards")
    thumbnail   = models.CharField(max_length=256, null=True)
    content     = models.TextField()
    rawContent  = models.TextField()

    class Meta:
        app_label = "World"


class MapPicture(models.Model):
    neGeoHash = models.CharField(max_length=16)
    swGeoHash = models.CharField(max_length=16)
    picWidth = models.IntegerField()
    picHeight = models.IntegerField()
    scale   = models.IntegerField()
    language = models.CharField(max_length=8)
    picture = models.CharField(max_length=256, null=True)

    class Meta:
        app_label = "World"

        unique_together = [
            ["neGeoHash", "swGeoHash", "picWidth", "picHeight", "scale", "language"]
        ]


class CountryFlag(models.Model):
    country = models.OneToOneField(Destination, related_name="flag", db_constraint=False)
    flagImage = models.CharField(max_length=64)

    class Meta:
        app_label = "World"


class CountryVisa(models.Model):
    country = models.OneToOneField(Destination, related_name="visa", db_constraint=False)
    content = models.TextField()

    class Meta:
        app_label = "World"
