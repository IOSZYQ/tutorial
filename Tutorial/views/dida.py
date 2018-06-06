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
        last, start, count = getPagePosition(request)

        hotels = didaApi.read(query={"checkIn": checkIn,
                                     "checkOut": checkOut,
                                     "star": star,
                                     "city": city}, start=start, count=count, last=last)
        return viewResponse({"hotels": hotels})


class DestinationUpdates(APIView):
    def get(self, request, format=None):
        dateFrom = request.GET.get("fromDate", None)
        country = request.GET.get("country", None)
        last, start, count = getPagePosition(request)

        destinationUpdates = destinationUpdateApi.read(query={
            "fromDate": dateFrom,
            "country": country
        }, fields=DestinationUpdateFields.brief, start=start, count=count, last=last)["updates"]
        return viewResponse({"updates": destinationUpdates})


class HotelUpdates(APIView):
    def get(self, request, format=None):
        dateFrom = request.GET.get("fromDate", None)
        last, start, count = getPagePosition(request)

        hotelUpdates = hotelUpdateApi.read(query={
            "fromDate": dateFrom
        },fields=HotelUpdateFields.brief, start=start, count=count, last=last)["updates"]
        return viewResponse({"updates": hotelUpdates})


class DestinationSync(APIView):
    def put(self, request, format=None):
        syncMap = request.data.get("syncMap")

        destinationUpdateApi.update(syncMap=syncMap)
        return viewResponse({})


class HotelSync(APIView):
    def put(self, request, format=None):
        syncMap = request.data.get("syncMap")

        hotelUpdateApi.update(syncMap=syncMap)
        return viewResponse({})
