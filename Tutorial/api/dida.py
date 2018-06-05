__author__ = "HanHui"

import apiUtils

from clients import DidaClient
from utilities import djangoUtils, utils
from Tutorial.models import Destination, Hotel
from Tutorial.elastic import searchHotels


def read(**kwargs):
    query = kwargs.get("query")
    checkIn = query.get("checkIn")
    checkOut = query.get("checkOut")
    cityId = query.get("city")
    star = query.get("star")
    last = kwargs.get("last", None)
    start = kwargs.get("start", 0)
    count = kwargs.get("count", 24)
    last = djangoUtils.decodeId(last) if last else 0

    destination = Destination.objects.filter(tosId=djangoUtils.decodeId(cityId), source="dida").first()
    if not destination:
        return {
            "priceList": [],
            "hasMore": False
        }

    def doSearchHotels(fetchStart, fetchTripCnt):
        return searchHotels(fetchStart, fetchTripCnt, longitude=destination.longitude, latitude=destination.latitude, distance=30000)

    hotelIds, hasMore, highlights, total = apiUtils.searchWithHighlights(last, start, count, doSearchHotels)
    hotels = Hotel.objects.filter(pk__in=hotelIds).all()
    tosIdMap = {hotel.sourceId: hotel.tosId for hotel in hotels}

    client = DidaClient()
    hotels = client.searchHotelPrices(checkIn, checkOut, hotelList=[int(hotel.sourceId) for hotel in hotels])
    hotelDict = {str(hotel["HotelID"]): hotel for hotel in hotels}

    hotelPrices = [{"price": hotelDict[sourceId]["LowestPrice"]["Value"],
                    "currency": utils.getCurrencyCode(hotelDict[sourceId]["LowestPrice"]["Currency"]),
                    "tosId": djangoUtils.encodeId(tosIdMap[sourceId]) if sourceId in tosIdMap else None} for sourceId in hotelDict]
    return {
        "priceList": hotelPrices,
        "hasMore": hasMore
    }
