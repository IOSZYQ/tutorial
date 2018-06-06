__author__ = "HanHui"

import json
import projectConfig

from datetime import datetime
from django.utils import timezone
from django.db import transaction
from collections import OrderedDict
from utilities import djangoUtils, utils

from Tutorial.models import DestinationUpdate, Destination
from Tutorial.serializers import DestinationUpdateSerializer


def read(**kwargs):
    query = kwargs.get('query', {})
    fields = kwargs.get('fields')
    updateIds = query.get('id')

    if updateIds:
        updateIds = djangoUtils.decodeIdList(updateIds)
        count = len(updateIds)
        total = count
        hasMore = False
        destinationUpdates = DestinationUpdate.objects.filter(pk__in=updateIds)
    else:
        destinationUpdates = DestinationUpdate.objects.filter()
        country = query.get("country", None)

        last = kwargs.get("last", None)
        start = kwargs.get("start", 0)
        count = kwargs.get("count", 24)
        last = djangoUtils.decodeId(last) if last else 0
        destinationUpdates = destinationUpdates.filter(pk__gt=last)
        if country is not None:
            isNull = True if country.lower() == "true" else False
            destinationUpdates = destinationUpdates.filter(sourceId__isnull=isNull)
        else:
            destinationUpdates = destinationUpdates.objects.filter(longitude__isnull=False,
                                                                   latitude__isnull=False)

        fromDate = query.get("fromDate")
        if fromDate is not None:
            fromDate = datetime.strptime(fromDate, projectConfig.DATE_FORMAT)
            destinationUpdates = destinationUpdates.filter(updated__gte=fromDate)

        destinationUpdates = destinationUpdates[start:start+count+1]
        total = destinationUpdates.count()
        if total > count:
            destinationUpdates = destinationUpdates[0:count]
            total = count
            hasMore = True
        else:
            hasMore = False

    data = [DestinationUpdateSerializer(destinationUpdate, fields=fields).data for destinationUpdate in destinationUpdates]
    return {
        "total": total,
        "hasMore": hasMore,
        "updates": data
    }


@transaction.atomic
def update(**kwargs):
    syncMap = kwargs.get("syncMap")
    updateIds = [djangoUtils.decodeId(updateId) for updateId in syncMap.keys()]

    destinationUpdates = {destinationUpdate.id: destinationUpdate for destinationUpdate in DestinationUpdate.objects.filter(pk__in=updateIds).all()}
    destinationList = []
    for updateId in syncMap:
        destinationUpdate = destinationUpdates[djangoUtils.decodeId(updateId)]

        jsonData = json.loads(destinationUpdate.json)
        name_cn = jsonData["name_cn"] if "name_cn" in jsonData else None
        name_en = jsonData["name_en"] if "name_en" in jsonData else None

        destination = Destination.objects.filter(sourceId=destinationUpdate.sourceId,
                                                 countryCode=destinationUpdate.countryCode,
                                                 source=destinationUpdate.source).first()

        versionData = OrderedDict([
            ("name_cn", name_cn),
            ("name_en", name_en),
        ])
        version = utils.generateVersion(versionData)
        if not destination:
            destination = Destination(source=destinationUpdate.source,
                                      sourceId=destinationUpdate.sourceId,
                                      name_cn=name_cn,
                                      name_en=name_en,
                                      longitude=destinationUpdate.longitude,
                                      latitude=destinationUpdate.latitude,
                                      countryCode=destinationUpdate.countryCode,
                                      adminLevel=1 if destinationUpdate.sourceId is None else 2,
                                      tosId=djangoUtils.decodeId(syncMap[updateId]),
                                      version=version)
            destinationList.append(destination)
        else:
            if name_cn:
                destination.name_cn = name_cn
            if name_en:
                destination.name_en = name_en
            destination.tosId = djangoUtils.decodeId(syncMap[updateId])
            destination.version = utils.generateVersion(versionData)
            destination.save()
    if destinationList:
        Destination.objects.bulk_create(destinationList)
