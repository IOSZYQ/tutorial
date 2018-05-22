__author__ = "HanHui"

from clients import DidaClient
from utilities import djangoUtils
from Tutorial.models import Destination, Hotel


def read(**kwargs):
    query = kwargs.get("query")
    checkIn = query.get("checkIn")
    checkOut = query.get("checkOut")
    cityId = query.get("city")
    star = query.get("star")
    start = kwargs.get("start")
    count = kwargs.get("count")

    city = City.objects.filter(destId=djangoUtils.decodeId(cityId)).first()
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
    hotelDict = {hotel["HotelID"]: hotel for hotel in hotels}

    hotels = Hotel.objects.filter(sourceId__in=hotelDict.keys()).all()
    return [{"name_en": hotel.name_en,
             "name_cn": hotel.name_cn,
             "price": hotelDict[hotel.sourceId]["LowestPrice"]["Value"],
             "currency": hotelDict[hotel.sourceId]["LowestPrice"]["Currency"],
             "sourceId": hotel.sourceId,
             "poiId": hotel.poiId
             } for hotel in hotels]
