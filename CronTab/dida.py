# -*- coding:utf-8 -*-
__author__ = 'HanHui'

from .celery import app
from scripts.dida import normalizeDidaHotel, downloadDidaStaticData, geocodeLocationWithMapApi

@app.task
def syncHotels():
    print("start downloading")
    downloadDidaStaticData()
    print("end downloading")

    print("start normalizing hotel")
    normalizeDidaHotel()
    print("end normalizing hotel")


@app.task
def gecodewithMapApi():
    print("start gecode")
    geocodeLocationWithMapApi()
    print("end gecode")
