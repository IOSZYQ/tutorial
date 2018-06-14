__author__ = 'HanHui'

import projectConfig

from django.utils import timezone

from utilities import DataSerializer, djangoUtils

from ..models import HotelUpdate
from .hotel import HotelSerializer
from ..dataFormat.hotel import HotelFields


class HotelUpdateSerializer(DataSerializer):
    def __init__(self, hotelUpdate, fields, parameters=None):
        if isinstance(hotelUpdate, int) or isinstance(hotelUpdate, str):
            hotelUpdate = HotelUpdate.objects.get(pk=hotelUpdate)

        super(HotelUpdateSerializer, self).__init__(hotelUpdate, fields, parameters)

        self._hotelUpdate = hotelUpdate

    def created(self, fields=None):
        return timezone.localtime(self._hotelUpdate.created).strftime(projectConfig.DATE_TIME_FORMAT)

    def updated(self, fields=None):
        return timezone.localtime(self._hotelUpdate.updated).strftime(projectConfig.DATE_TIME_FORMAT)

    def hotel(self, fields=None):
        if fields == True:
            return djangoUtils.encodeId(self._hotelUpdate.hotel_id)
        return HotelSerializer(hotel=self._hotelUpdate.hotel, fields=HotelFields.brief)
