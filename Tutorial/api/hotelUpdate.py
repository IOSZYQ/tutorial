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
        countryCode = jsonData["countryCode"] if "countryCode" in jsonData else None

        hotel = Hotel.objects.filter(sourceId=hotelUpdate["sourceId"], source=hotelUpdate["source"]).first()
        if not hotel:
            hotel = Hotel.objects.create(source=hotelUpdate["source"],
                                         sourceId=hotelUpdate["sourceId"],
                                         name_cn=name_cn,
                                         name_en=name_en,
                                         countryCode=countryCode,
                                         adminLevel=1 if hotelUpdate.sourceId is None else 2,
                                         tosId=djangoUtils.decodeId(syncMap[updateId]))
        else:
            if name_cn:
                hotel.name_cn = name_cn
            if name_en:
                hotel.name_en = name_en
            if countryCode:
                hotel.countryCode = countryCode
        versionData = OrderedDict([
            ("name_cn", name_cn),
            ("name_en", name_en),
            ("countryCode", countryCode)
        ])
        hotel.version = utils.generateVersion(versionData)
        hotel.save()
