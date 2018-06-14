__author__ = 'HanHui'

import projectConfig

from django.utils import timezone

from utilities import DataSerializer, djangoUtils

from ..models import Hotel
from .destination import DestinationSerializer
from ..dataFormat.destination import DestinationFields


class HotelSerializer(DataSerializer):
    def __init__(self, hotel, fields, parameters=None):
        if isinstance(hotel, int) or isinstance(hotel, str):
            hotel = Hotel.objects.get(pk=hotel)

        super(HotelSerializer, self).__init__(hotel, fields, parameters)

        self._hotel = hotel

    def created(self, fields=None):
        return timezone.localtime(self._hotel.created).strftime(projectConfig.DATE_TIME_FORMAT)

    def updated(self, fields=None):
        return timezone.localtime(self._hotel.updated).strftime(projectConfig.DATE_TIME_FORMAT)

    def destination(self, fields=None):
        if fields == True:
            return djangoUtils.encodeId(self._hotel.destination_id)
        return DestinationSerializer(destination=self._hotel.destination, fields=DestinationFields.brief).data
