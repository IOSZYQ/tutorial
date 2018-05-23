__author__ = "HanHui"

from django.db import models


class Dida(models.Model):
    countryFilePath    = models.FilePathField(null=True)
    cityFilePath       = models.FilePathField(null=True)
    hotelFilePath      = models.FilePathField(null=True)
    created            = models.DateTimeField(auto_now_add=True)
    normalizeTime      = models.DateTimeField(null=True)
