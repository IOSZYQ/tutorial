__author__ = 'HanHui'

from . import config
from Tutorial.models import Hotel
from itertools import groupby
from elasticsearch import helpers
from django.db.models import QuerySet
import elasticUtils, elasticInlines


def _hotelDoc(hotel, fields=None):
    hotelDoc = {
        "name_en"           : hotel.name_en,
        "name_cn"           : hotel.name_cn,
        "source"            : hotel.source,
        "sourceId"          : hotel.sourceId,
        "tosId"             : hotel.tosId,
        "cityId"            : hotel.cityId,
        "address"           : hotel.address,
        "location"          : {"lat": hotel.latitude, "lon": hotel.longitude} if hotel.latitude and hotel.longitude else None,
        "starRating"        : float(hotel.starRating),
        "created"           : hotel.created
    }
    return hotelDoc


def updateHotel(hotels, updatedFields):
    hotels = hotels if isinstance(hotels, (list, tuple, set, QuerySet)) else [hotels]
    if not hotels:
        return

    es = elasticUtils.getClient()

    actions = []
    for hotel in hotels:
        if hotel.inactive:
            es.delete(index="lushu_hotels", doc_type='poi', id=hotel.id, ignore=404, refresh=True)
        else:
            actions.append({
                "_op_type": "update",
                "_index": "lushu_hotels",
                "_type": "hotel",
                "_id": hotel.id,
                "doc": _hotelDoc(hotel, fields=updatedFields)
            })

    if actions:
        try:
            helpers.bulk(es, actions)
        except:
            indexHotel(hotels)


def indexHotel(hotels):
    hotels = hotels if isinstance(hotels, (list, tuple, set, QuerySet)) else [hotels]
    if not hotels:
        return

    if isinstance(hotels[0], int) or isinstance(hotels[0], str):
        hotels = Hotel.objects.filter(pk__in=hotels)

    es = elasticUtils.getClient()

    actions = []
    for hotel in hotels:
        if hotel.inactive:
            es.delete(index="lushu_hotels", doc_type='hotel', id=hotel.id, ignore=404, refresh=True)
        else:
            actions.append({
                "_op_type": "index",
                "_index": "lushu_hotels",
                "_type": "hotel",
                "_id": hotel.id,
                "_source": _hotelDoc(hotel)
            })

    if actions:
        helpers.bulk(elasticUtils.getClient(), actions)


def indexAllHotels():
    elasticUtils.resetIndex("lushu_hotels", config)

    latestHotel = Hotel.objects.order_by("-id").first()
    lastHotelId = 0

    while lastHotelId <= latestHotel.id:
        allHotels = Hotel.objects.filter(id__gt=lastHotelId, id__lte=lastHotelId + 10000)
        if len(allHotels) == 0:
            break

        actions = []
        for hotel in allHotels:
            if not hotel.inactive:
                actions.append({
                    '_op_type': 'index',
                    '_index': 'lushu_hotels',
                    '_type': 'hotel',
                    '_id': hotel.id,
                    '_source': _hotelDoc(hotel)
                })

        helpers.bulk(elasticUtils.getClient(), actions)

        lastHotelId = max(hotel.id for hotel in allHotels)


def searchHotels(start=0, count=10, latitude=None, longitude=None, distance=1000, star=None, q="", highlightFields=None, order=None):
    hotelQuery = {"match_all": {}} if not q else {
        "multi_match": {
            "query"                 : q,
            "type"                  : "best_fields",
            "fields"                : [ "name_en", "name_cn" ],
            "tie_breaker"           : 0.55,
            "minimum_should_match"  : "30%",
            "boost"                 : 10
        }
    }

    filters = []
    if latitude != None and longitude != None and distance > 0:
        filters.append({
            "geo_distance": {
                "location": {
                    "lat": latitude,
                    "lon": longitude
                },
                "distance": "{0}m".format(distance),
                "distance_type": "plane"
            }
        })

    hotelQuery = elasticUtils.filteredQuery(hotelQuery, filters)
    highlight = {
        "fields" : { field:{} for field in highlightFields }
    } if highlightFields and q else None

    return elasticUtils.doSearch(hotelQuery, start, count, order, "lushu_hotels", "hotel", highlight=highlight)
