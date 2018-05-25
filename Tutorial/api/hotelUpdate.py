__author__ = "HanHui"

import projectConfig

from datetime import datetime
from utilities import djangoUtils
from Tutorial.models import HotelUpdate
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
