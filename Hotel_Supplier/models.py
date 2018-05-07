from django.db import models

class DidaCountry(models.Model):
    sourceId       = models.CharField(max_length=10, unique=True)
    name_cn        = models.CharField(max_length=64, default="")
    name_en        = models.CharField(max_length=64, default="")
    destId         = models.IntegerField(null=True)
    inactive       = models.BooleanField(default=False)
    created        = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "Hotel_Supplier"

        index_together = [
            ["inactive", "destId"]
        ]


class DidaCity(models.Model):
    country        = models.ForeignKey(DidaCountry, related_name="cities", on_delete=models.CASCADE)
    sourceId       = models.CharField(max_length=10, unique=True)
    name_cn        = models.CharField(max_length=128, default="")
    name_en        = models.CharField(max_length=64, default="")
    destId         = models.IntegerField(null=True)
    inactive       = models.BooleanField(default=False)
    created        = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "Hotel_Supplier"

        index_together = [
            ["inactive", "destId"]
        ]


class DidaBedType(models.Model):
    typeId         = models.IntegerField(unique=True)
    defaultOccupancy = models.IntegerField()
    name_cn        = models.CharField(max_length=64, default="")
    name_en        = models.CharField(max_length=64, default="")
    inactive       = models.BooleanField(default=False)
    created        = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "Hotel_Supplier"


class DidaBreakfastType(models.Model):
    typeId         = models.IntegerField(unique=True)
    name_cn        = models.CharField(max_length=64, default="")
    name_en        = models.CharField(max_length=64, default="")
    inactive       = models.BooleanField(default=False)
    created        = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "Hotel_Supplier"


class DidaHotel(models.Model):
    city           = models.ForeignKey(DidaCity, related_name="hotels", on_delete=models.CASCADE)
    sourceId       = models.IntegerField(unique=True)
    name           = models.CharField(max_length=128, default="")
    address        = models.CharField(max_length=1024, null=True)
    zipCode        = models.CharField(max_length=32, null=True)
    latitude       = models.FloatField()
    longitude      = models.FloatField()
    geohash8       = models.CharField(max_length=16, db_index=True)
    starRating     = models.IntegerField()
    telephone      = models.CharField(max_length=32, null=True)
    amenity        = models.TextField(null=True)
    rooms          = models.TextField(null=True)
    inactive       = models.BooleanField(default=False)
    created        = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "Hotel_Supplier"


class DidaPoiHotel(models.Model):
    poiId          = models.IntegerField(db_index=True)
    hotel          = models.ForeignKey(DidaHotel, related_name="+", on_delete=models.CASCADE)
    public         = models.BooleanField(default=False)

    class Meta:
        app_label = "Hotel_Supplier"

        unique_together = [
            ["poiId", "hotel"]
        ]