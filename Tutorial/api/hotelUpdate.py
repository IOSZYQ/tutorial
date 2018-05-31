__author__ = "HanHui"

import json
import projectConfig

from datetime import datetime
from utilities import djangoUtils, utils
from django.db import transaction
from collections import OrderedDict

from Tutorial.models import HotelUpdate, Hotel
from Tutorial.serializers import HotelUpdateSerializer


def read(**kwargs):
    query = kwargs.get('query', {})
    fields = kwargs.get('fields')
    updateIds = query.get('id')

    if updateIds:
        updateIds = djangoUtils.decodeIdList(updateIds)
        count = len(updateIds)
        total = count
        hasMore = False
        hotelUpdates = HotelUpdate.objects.filter(pk__in=updateIds)
    else:
        hotelUpdates = HotelUpdate.objects.all()

        last = kwargs.get("last", None)
        start = kwargs.get("start", 0)
        count = kwargs.get("count", 24)
        last = djangoUtils.decodeId(last) if last else 0
        hotelUpdates = hotelUpdates.filter(pk__gt=last)

        dateFrom = query.get("dateFrom")
        if dateFrom is not None:
            dateFrom = datetime.strptime(dateFrom, projectConfig.DATE_FORMAT)
            hotelUpdates = hotelUpdates.filter(updated__gte=dateFrom)

        hotelUpdates = hotelUpdates[start:start+count+1]
        total = hotelUpdates.count()
        if total > count:
            hotelUpdates = hotelUpdates[0:count]
            total = count
            hasMore = True
        else:
            hasMore = False

    data = [HotelUpdateSerializer(hotelUpdate, fields=fields).data for hotelUpdate in hotelUpdates]
    return {
        "total": total,
        "hasMore": hasMore,
        "updates": data
    }



@transaction.atomic
def update(**kwargs):
    syncMap = kwargs.get("syncMap")
    updateIds = [djangoUtils.decodeId(updateId) for updateId in syncMap.keys()]

    hotelUpdates = {hotelUpdate.id: hotelUpdate for hotelUpdate in HotelUpdate.objects.filter(pk__in=updateIds).all()}
    for updateId in syncMap:
        hotelUpdate = hotelUpdates[djangoUtils.decodeId(updateId)]

        jsonData = json.loads(hotelUpdate.json)
        name_cn = jsonData["name_cn"] if "name_cn" in jsonData else None
        name_en = jsonData["name_en"] if "name_en" in jsonData else None
        cityId = jsonData["cityId"] if "cityId" in jsonData else None
        address = jsonData["address"] if "address" in jsonData else None
        zipCode = jsonData["zipCode"] if "zipCode" in jsonData else None
        latitude = jsonData["latitude"] if "latitude" in jsonData else None
        longitude = jsonData["longitude"] if "longitude" in jsonData else None
        geohash8 = jsonData["geohash8"] if "geohash8" in jsonData else None
        starRating = jsonData["starRating"] if "starRating" in jsonData else None
        telephone = jsonData["telephone"] if "telephone" in jsonData else None
        amenity = jsonData["amenity"] if "amenity" in jsonData else None
        rooms = jsonData["rooms"] if "rooms" in jsonData else None

        hotel = Hotel.objects.filter(sourceId=hotelUpdate.sourceId, source=hotelUpdate.source).first()
        if not hotel:
            hotel = Hotel.objects.create(source=hotelUpdate.source,
                                         sourceId=hotelUpdate.sourceId,
                                         name_cn=name_cn,
                                         name_en=name_en,
                                         cityId=cityId,
                                         address=address,
                                         latitude=latitude,
                                         longitude=longitude,
                                         geohash8=geohash8,
                                         telephone=telephone,
                                         starRating=starRating,
                                         amenity=amenity,
                                         rooms=rooms,
                                         tosId=djangoUtils.decodeId(syncMap[updateId]))
        else:
            if name_cn:
                hotel.name_cn = name_cn
            if name_en:
                hotel.name_en = name_en
            if address:
                hotel.address = address
            if cityId:
                hotel.cityId = cityId
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
            hotel.tosId = djangoUtils.decodeId(syncMap[updateId])

        versionData = OrderedDict([("name_cn", name_cn),
                                   ("name_en", name_en),
                                   ("address", address),
                                   ("cityId", cityId),
                                   ("zipCode", zipCode),
                                   ("longitude", longitude),
                                   ("latitude", latitude),
                                   ("starRating", starRating),
                                   ("telephone", telephone)])
        hotel.version = utils.generateVersion(versionData)
        hotel.save()
