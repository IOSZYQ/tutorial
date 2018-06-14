__author__ = "HanHui"

import apiUtils
import projectConfig

from datetime import datetime
from utilities import djangoUtils

from Tutorial.models import HotelUpdate
from Tutorial.api import hotel as hotelApi
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
        hotelUpdates = HotelUpdate.objects.filter()

        last = kwargs.get("last", None)
        start = kwargs.get("start", 0)
        count = kwargs.get("count", 24)
        last = djangoUtils.decodeId(last) if last else 0
        hotelUpdates = hotelUpdates.filter(pk__gt=last)

        fromDate = query.get("date")
        if fromDate is not None:
            fromDate = datetime.strptime(fromDate, projectConfig.DATE_FORMAT)
            hotelUpdates = hotelUpdates.filter(updated__gte=fromDate)

        hotelUpdates = hotelUpdates.prefetch_related("hotel")
        hotelUpdates = hotelUpdates[start:start+count+1]
        total = hotelUpdates.count()
        if total > count:
            hotelUpdates = hotelUpdates[0:count]
            total = count
            hasMore = True
        else:
            hasMore = False

    relatedFields = apiUtils.popFields(fields, ['hotel'])
    updateData = [HotelUpdateSerializer(hotelUpdate, fields=fields).data for hotelUpdate in hotelUpdates]
    hotelIds = djangoUtils.combineHashes(apiUtils.collectValues(updateData, ["hotel"]))
    if hotelIds and relatedFields.get("hotel"):
        hotels = hotelApi.read(query={"id": hotelIds}, fields=relatedFields["hotel"])
        hotelDict = {hotel["id"]: hotel for hotel in hotels}
        apiUtils.updateFieldValue(updateData, ["hotel"], relatedFields, hotelDict)

    return {
        "total": total,
        "hasMore": hasMore,
        "updates": updateData
    }
