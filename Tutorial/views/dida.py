__author__ = "HanHui"

from rest_framework.views import APIView
from utilities.viewUtils import viewResponse

from Tutorial.api import dida as didaApi


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
