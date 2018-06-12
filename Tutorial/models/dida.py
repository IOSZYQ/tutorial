__author__ = "HanHui"

from django.db import models


class Dida(models.Model):
    countryFile        = models.FilePathField(null=True)
    cityFile           = models.FilePathField(null=True)
    hotelFile          = models.FilePathField(null=True)
    created            = models.DateTimeField(auto_now_add=True)
