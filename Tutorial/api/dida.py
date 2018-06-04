__author__ = "HanHui"

from clients import DidaClient
from utilities import djangoUtils, utils
from Tutorial.models import Destination, Hotel


def read(**kwargs):
    query = kwargs.get("query")
    checkIn = query.get("checkIn")
    checkOut = query.get("checkOut")
    cityId = query.get("city")
    star = query.get("star")
    start = kwargs.get("start")
    count = kwargs.get("count")

    city = Destination.objects.filter(tosId=djangoUtils.decodeId(cityId), adminLevel=2).first()
    if not city:
        return []

    pageNum = None
    countPerPage = None
    if start is not None and count is not None:
        start = int(start)
        count = int(count)
        countPerPage = count
        pageNum = int(start / count + 1)

    client = DidaClient()
    hotels = client.searchHotelPrices(checkIn, checkOut, str(city.sourceId), star, countPerPage, pageNum)
    hotelDict = {str(hotel["HotelID"]): hotel for hotel in hotels}

    hotels = Hotel.objects.filter(sourceId__in=hotelDict.keys()).all()
    tosIdMap = {hotel.sourceId: hotel.tosId for hotel in hotels}
    return [{"name": hotelDict[sourceId]["HotelName"],
             "price": hotelDict[sourceId]["LowestPrice"]["Value"],
             "currency": utils.getCurrencyCode(hotelDict[sourceId]["LowestPrice"]["Currency"]),
             "sourceId": sourceId,
             "tosId": djangoUtils.encodeId(tosIdMap[sourceId]) if sourceId in tosIdMap else None} for sourceId in hotelDict]
