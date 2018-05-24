__author__ = "HanHui"

from rest_framework.views import APIView
from utilities.viewUtils import viewResponse, getPagePosition

from Tutorial.dataFormat import DestinationUpdateFields, HotelUpdateFields
from Tutorial.api import didaApi, destinationUpdateApi, hotelUpdateApi


class HotelFind(APIView):
    def get(self, request, format=None):
        checkIn = request.GET.get("checkIn", None)
        checkOut = request.GET.get("checkOut", None)
        star = request.GET.get("star", None)
        city = request.GET.get("city", None)
        start = request.GET.get("start", None)
        count = request.GET.get("count", None)

        hotels = didaApi.read(query={"checkIn": checkIn,
                                     "checkOut": checkOut,
                                     "star": star,
                                     "city": city}, start=start, count=count)
        return viewResponse({"hotels": hotels})


class DestinationUpdates(APIView):
    def get(self, request, format=None):
        last, start, count = getPagePosition(request)

        destinationUpdates = destinationUpdateApi.read(fields=DestinationUpdateFields.brief, start=start, count=count, last=last)["updates"]
        return viewResponse({"updates": destinationUpdates})


class HotelUpdates(APIView):
    def get(self, request, format=None):
        last, start, count = getPagePosition(request)

        hotelUpdates = hotelUpdateApi.read(fields=HotelUpdateFields.brief, start=start, count=count, last=last)["updates"]
        return viewResponse({"updates": hotelUpdates})
