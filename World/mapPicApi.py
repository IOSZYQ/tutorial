__author__ = 'swolfod'

from .models import *
from utilities import djangoUtils, utils
import images.utils
from Geohash import geohash
from django.conf import settings
from django.db import transaction


@transaction.atomic
def read(**kwargs):
    query = kwargs.get("query", {})
    latN = query.get("latN")
    latS = query.get("latS")
    lngE = query.get("lngE")
    lngW = query.get("lngW")

    if latN == None or latS == None or lngE == None or lngW == None:
        destinationId = query.get("destinationId")
        if destinationId:
            destination = Destination.objects.get(pk=djangoUtils.decodeId(destinationId))
            latN = destination.latitudeN
            latS = destination.latitudeS
            lngE = destination.longitudeE
            lngW = destination.longitudeW

    if latN == None or latS == None or lngE == None or lngW == None:
        return None

    width = kwargs.get("width", 420)
    height = kwargs.get("height", 420)
    scale = kwargs.get("scale", 1)
    precision = kwargs.get("precision", 8)

    neGeohash = geohash.encode(float(latN), float(lngE), precision=precision)
    swGeohash = geohash.encode(float(latS), float(lngW), precision=precision)
    mapPic = MapPicture.objects.filter(neGeoHash=neGeohash, swGeoHash=swGeohash, picWidth=width, picHeight=height,
                                       scale=scale, language=settings.GOOGLE_LANGUAGE_CODE).first()
    if mapPic:
        return mapPic.picture

    mapPic = MapPicture(neGeoHash=neGeohash, swGeoHash=swGeohash, picWidth=width, picHeight=height,
                        scale=1, language=settings.GOOGLE_LANGUAGE_CODE)

    hashN, hashE, neDiffLat, neDiffLng = geohash.decode_exactly(neGeohash)
    picN = hashN + neDiffLat
    picE = hashE + neDiffLng
    if picN > 90:
        picN = 90
    if picE > 180:
        picE -= 360

    hashS, hashW, swDiffLat, swDiffLng = geohash.decode_exactly(swGeohash)
    picS = hashS - swDiffLat
    picW = hashW - swDiffLng
    if picS < -90:
        picS = -90
    if picW < -180:
        picW += 360

    zoom = utils.getGoogleMapZoom(picN, picE, picS, picW, width, height)
    mapLat = (picN + picS) / 2
    mapLng = (picE + picW) / 2
    if mapLng < -180:
        mapLng += 360
    if mapLng > 180:
        mapLng -= 360

    picUrl = utils.getGoogleStaticMapUrl(mapLat, mapLng, zoom, width, height, 1, settings.GOOGLE_LANGUAGE_CODE)
    mapPic.picture = images.utils.loadImageFromUrl(
        picUrl,fileName="{0}_{1}_{2}x{3}_{4}_{5}"
        .format(neGeohash, swGeohash, width, height, scale, settings.GOOGLE_LANGUAGE_CODE.replace('-', '_')), static=True)

    mapPic.save()

    return mapPic.picture