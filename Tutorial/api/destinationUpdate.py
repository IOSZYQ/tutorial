__author__ = "HanHui"

from utilities import djangoUtils
from Tutorial.models import DestinationUpdate
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
        destinationUpdates = DestinationUpdate.objects.all()

        last = kwargs.get("last", None)
        start = kwargs.get("start", 0)
        count = kwargs.get("count", 24)
        last = djangoUtils.decodeId(last) if last else 0
        destinationUpdates = destinationUpdates.filter(pk__gt=last)[start:start + count + 1]

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
