__author__ = 'swolfod'

from django.db import transaction
from django.db.models import Q, F
from django.http import *
from .models import Destination, DestinationShape
from utilities import djangoUtils, utils
from .dataFormat import *
from .serializers import DestinationSerializer


def read(**kwargs):
    query = kwargs.get("query", {})
    fields = kwargs.get("fields")
    parameters = kwargs.get("serialization_paramters")
    refresh = kwargs.get("refresh")

    if not fields:
        fields = DestinationFields.full

    destIds = query.get("id")
    queryIds = []
    dataDict = {}

    cacheClient = djangoUtils.getCacheClient()

    if query.get("creatorId"):
        destQuery = Destination.objects.filter(inactive=False, creatorId=djangoUtils.decodeId(query["creatorId"]))
        destIds = djangoUtils.encodeIdList(list(destQuery.values_list("id", flat=True)))

    lat = query.get("latitude")
    lng = query.get("longitude")

    if lat != None and lng != None:
        gridNorth = lat + 0.4
        gridSouth = lat - 0.4
        gridEast = lng + 0.4
        gridWest = lng - 0.4

        if gridEast > 180:
            gridEast -= 360

        if gridWest < -180:
            gridWest += 360

        destQuery = Destination.objects.filter(inactive=False).filter(latitudeN__gte=gridSouth, latitudeS__lt=gridNorth)

        if gridEast >= gridWest:
            destQuery = destQuery.filter((Q(longitudeE__gte=F("longitudeW")) & Q(longitudeE__gte=gridWest) & Q(longitudeW__lt=gridEast)) \
                    | (Q(longitudeE__lt=F("longitudeW")) & (Q(longitudeE__gte=gridWest) | Q(longitudeW__lt=gridEast))))
        else:
            destQuery = destQuery.filter(Q(longitudeE__lt=F("longitudeW")) | Q(longitudeE__gte=gridWest) | Q(longitudeW__lt=gridEast))

        type = query.get("type")
        if type != None:
            destQuery = destQuery.filter(adminLevel=type)
        else:
            destQuery = destQuery.filter(adminLevel__in=[1,2])

        destIds = djangoUtils.encodeIdList(list(destQuery.order_by("adminLevel").values_list("id", flat=True)[:24]))

    if destIds:
        destIds = djangoUtils.decodeIdList(destIds)
        if query.get("timeStamp") is not None:
            destIds = sorted(Destination.objects.filter(pk__in=destIds, timeStamp__gte=query["timeStamp"]).values_list("id", flat=True),
                             key=lambda destId: destIds.index(destId))

        for destId in destIds:
            destInfo = None

            if not refresh:
                dataKey = "destination-{0}".format(destId)
                destInfo = cacheClient.get(dataKey)

            if destInfo:
                dataDict[destId] = destInfo
            else:
                queryIds.append(destId)

    if destIds == None or queryIds:
        destQuery = Destination.objects.select_related("parent").select_related("flag").prefetch_related("aliases", "cards", "infos")
        if queryIds:
            destQuery = destQuery.filter(pk__in=queryIds)

        dataSet = destQuery.all()

        dataDict.update({ destination.id: DestinationSerializer(destination, DestinationFields.allFields, parameters).data for destination in dataSet })

        for destId in queryIds:
            if destId not in dataDict:
                continue
            cacheClient.set("destination-{0}".format(destId), dataDict[destId], timeout=10800)

    destinations = []
    dataList = list(dataDict.items())
    if destIds:
        dataList.sort(key=lambda destTuple: destIds.index(destTuple[0]))

    for destId, data in dataList:
        if fields.get("shape"):
            shapePoints = DestinationShape.objects.filter(destination_id=destId).order_by("index").all()
            data["shape"] = [{
                "latitude"  : point.latitude,
                "longitude" : point.longitude
            } for point in shapePoints]

        destinations.append(utils.extractData(data, fields))


    return destinations


@transaction.atomic
def create(**kwargs):
    creatorId = kwargs.get("creatorId")
    type = kwargs["type"]
    name = kwargs["name"].strip()
    name_cn = (kwargs.get("name_cn") or "").strip()
    name_en = (kwargs.get("name_en") or "").strip()
    iso = (kwargs.get("iso") or "").strip() or None
    iso2 = (kwargs.get("iso2") or "").strip() or None
    sovereignty = (kwargs.get("sovereignty") or "").strip() or None
    parentId = kwargs.get("parent")
    latitude = kwargs["latitude"]
    longitude = kwargs["longitude"]
    latitudeN = kwargs.get("latitudeN")
    longitudeE = kwargs.get("longitudeE")
    latitudeS = kwargs.get("latitudeS")
    longitudeW = kwargs.get("longitudeW")
    public = kwargs.get("public")

    creatorId = djangoUtils.decodeId(creatorId)

    if type < 0 or type > 2:
        raise Http404

    parent = None
    if parentId:
        parentId = djangoUtils.decodeId(parentId)
        parent = Destination.objects.get(pk=parentId)
        if parent.adminLevel != type - 1:
            raise Http404
    elif type != 0:
        raise Http404


    if latitudeN is None:
        latitudeN = latitude + 0.07
    if latitudeN > 85:
        latitudeN = 85

    if latitudeS is None:
        latitudeS = latitude - 0.07
    if latitudeS < -85:
        latitudeS = -85

    if longitudeE is None:
        longitudeE = longitude + 0.1
    if longitudeE > 180:
        longitudeE -= 360

    if longitudeW is None:
        longitudeW = longitude - 0.1
    if longitudeW < -180:
        longitudeW += 360

    destination = Destination(
        creatorId=creatorId,
        adminLevel=type,
        name=name,
        latitude = latitude,
        longitude=longitude,
        latitudeN=latitudeN,
        latitudeS=latitudeS,
        longitudeE=longitudeE,
        longitudeW=longitudeW,
        shapeN=latitudeN,
        shapeS=latitudeS,
        shapeE=longitudeE,
        shapeW=longitudeW,
        parent=parent,
        ISO=iso or parent.ISO,
        ISO2=iso2 or parent.ISO2,
        sovereignty=sovereignty or parent.sovereignty
    )

    if name_cn:
        destination.name_cn = name_cn

    if name_en:
        destination.name_en = name_en

    if public is not None:
        destination.public = public

    destination.timeStamp = djangoUtils.getCurrentTimeStamp()
    destination.save()
    return djangoUtils.encodeId(destination.id)
