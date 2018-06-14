__author__ = "HanHui"

import apiUtils
import projectConfig

from datetime import datetime
from utilities import djangoUtils

from Tutorial.models import DestinationUpdate
from Tutorial.serializers import DestinationUpdateSerializer
from Tutorial.api import destination as destinationApi


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
        destinationUpdates = DestinationUpdate.objects.filter(destination__longitude__isnull=False,
                                                              destination__latitude__isnull=False)
        country = query.get("country", None)

        last = kwargs.get("last", None)
        start = kwargs.get("start", 0)
        count = kwargs.get("count", 24)
        last = djangoUtils.decodeId(last) if last else 0
        destinationUpdates = destinationUpdates.filter(pk__gt=last)
        if country is not None:
            isCountry = True if country.lower() == "true" else False
            destinationUpdates = destinationUpdates.filter(destination__adminLevel=1 if isCountry else 2)

        fromDate = query.get("date")
        if fromDate is not None:
            fromDate = datetime.strptime(fromDate, projectConfig.DATE_FORMAT)
            destinationUpdates = destinationUpdates.filter(updated__gte=fromDate)

        destinationUpdates = destinationUpdates.prefetch_related("destination")
        destinationUpdates = destinationUpdates[start:start+count+1]
        total = destinationUpdates.count()
        if total > count:
            destinationUpdates = destinationUpdates[0:count]
            total = count
            hasMore = True
        else:
            hasMore = False

    relatedFields = apiUtils.popFields(fields, ['destination'])
    updateData = [DestinationUpdateSerializer(destinationUpdate, fields=fields).data for destinationUpdate in destinationUpdates]
    destinationIds = djangoUtils.combineHashes(apiUtils.collectValues(updateData, ["destination"]))
    if destinationIds and relatedFields.get("destination"):
        destinations = destinationApi.read(query={"id": destinationIds}, fields=relatedFields["destination"])
        destinationDict = {destination["id"]: destination for destination in destinations}
        apiUtils.updateFieldValue(updateData, ["destination"], relatedFields, destinationDict)

    return {
        "total": total,
        "hasMore": hasMore,
        "updates": updateData
    }
