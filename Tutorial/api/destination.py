__author__ = "HanHui"

import json

from django.db import transaction
from utilities import djangoUtils, utils

from Tutorial.models import Destination
from Tutorial.serializers import DestinationSerializer


def read(**kwargs):
    query = kwargs.get('query', {})
    fields = kwargs.get('fields')
    destinationIds = query.get('id')

    destinationIds = djangoUtils.decodeIdList(destinationIds)
    destinations = Destination.objects.filter(pk__in=destinationIds).prefetch_related("parent")
    return [DestinationSerializer(destination, fields=fields).data for destination in destinations]


@transaction.atomic
def update(**kwargs):
    syncMap = kwargs.get("syncMap")
    updateIds = [djangoUtils.decodeId(updateId) for updateId in syncMap.keys()]

    destinationMap = {djangoUtils.encodeId(destination.id): destination for destination in Destination.objects.filter(pk__in=updateIds).all()}
    for updateId in syncMap:
        jsonData = json.loads(syncMap[updateId]["json"])
        name_cn = jsonData["name_cn"] if "name_cn" in jsonData else None
        name_en = jsonData["name_en"] if "name_en" in jsonData else None
        longitude = syncMap[updateId]["destination"]["longitude"]
        latitude = syncMap[updateId]["destination"]["latitude"]
        longitudeE = syncMap[updateId]["destination"]["longitudeE"]
        longitudeW = syncMap[updateId]["destination"]["longitudeW"]
        latitudeS = syncMap[updateId]["destination"]["latitudeS"]
        latitudeN = syncMap[updateId]["destination"]["latitudeN"]

        tosId = djangoUtils.decodeId(syncMap[updateId]["destination"]["tosId"])

        destination = destinationMap[updateId]
        versionData = [
            ("name_cn", name_cn),
            ("name_en", name_en),
        ]
        version = utils.generateVersion(versionData)
        if name_cn:
            destination.name_cn = name_cn
        if name_en:
            destination.name_en = name_en
        if tosId:
            destination.tosId = tosId
        if latitude:
            destination.latitude = latitude
        if longitude:
            destination.longitude = longitude
        if longitudeE:
            destination.longitudeE = longitudeE
        if longitudeW:
            destination.longitudeW = longitudeW
        if latitudeS:
            destination.latitudeS = latitudeS
        if latitudeN:
            destination.latitudeN = latitudeN
        destination.version = version
        destination.save()
