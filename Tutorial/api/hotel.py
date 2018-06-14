__author__ = "HanHui"

import json
import apiUtils
import projectConfig

from datetime import datetime
from django.db import transaction
from utilities import djangoUtils, utils

from Tutorial.models import Hotel
from Tutorial.serializers import HotelSerializer
from Tutorial.api import destination as destinationApi


def read(**kwargs):
    query = kwargs.get('query', {})
    fields = kwargs.get('fields')
    hotelIds = query.get('id')

    hotelIds = djangoUtils.decodeIdList(hotelIds)
    hotels = Hotel.objects.filter(pk__in=hotelIds)

    relatedFields = apiUtils.popFields(fields, ['destination'])
    hotelData = [HotelSerializer(hotel, fields=fields).data for hotel in hotels]
    destinationIds = djangoUtils.combineHashes(apiUtils.collectValues(hotelData, ["destination"]))
    if destinationIds and relatedFields.get("destination"):
        destinations = destinationApi.read(query={"id": destinationIds}, fields=relatedFields["destination"])
        destinationDict = {destination["id"]: destination for destination in destinations}
        apiUtils.updateFieldValue(hotelData, ["destination"], relatedFields, destinationDict)
    return hotelData


@transaction.atomic
def update(**kwargs):
    syncMap = kwargs.get("syncMap")
    updateIds = [djangoUtils.decodeId(updateId) for updateId in syncMap.keys()]

    hotels = {djangoUtils.encodeId(hotel.id): hotel for hotel in Hotel.objects.filter(pk__in=updateIds).all()}
    for updateId in syncMap:
        jsonData = syncMap[updateId]
        name_cn = jsonData["name_cn"] if "name_cn" in jsonData else None
        name_en = jsonData["name_en"] if "name_en" in jsonData else None
        address = jsonData["address"] if "address" in jsonData else None
        zipCode = jsonData["zipCode"] if "zipCode" in jsonData else None
        latitude = jsonData["latitude"] if "latitude" in jsonData else None
        longitude = jsonData["longitude"] if "longitude" in jsonData else None
        geohash8 = jsonData["geohash8"] if "geohash8" in jsonData else None
        starRating = jsonData["starRating"] if "starRating" in jsonData else None
        telephone = jsonData["telephone"] if "telephone" in jsonData else None
        tosId = djangoUtils.decodeId(jsonData["tosId"]) if "tosId" in jsonData else None

        versionData = [("name_cn", name_cn),
                       ("name_en", name_en),
                       ("address", address),
                       ("zipCode", zipCode),
                       ("longitude", longitude),
                       ("latitude", latitude),
                       ("starRating", starRating),
                       ("telephone", telephone)]
        version = utils.generateVersion(versionData)
        hotel = hotels[updateId]
        if name_cn:
            hotel.name_cn = name_cn
        if name_en:
            hotel.name_en = name_en
        if address:
            hotel.address = address
        if zipCode:
            hotel.zipCode = zipCode
        if longitude:
            hotel.longitude = longitude
        if latitude:
            hotel.latitude = latitude
        if starRating:
            hotel.starRating = starRating
        if telephone:
            hotel.telephone = telephone
        if tosId:
            hotel.tosId = djangoUtils.decodeId(tosId)
        hotel.version = version
        hotel.save()
