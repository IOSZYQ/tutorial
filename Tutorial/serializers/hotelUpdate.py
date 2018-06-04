__author__ = 'HanHui'

import projectConfig

from django.utils import timezone

from utilities import DataSerializer, djangoUtils

from ..models import HotelUpdate, Hotel, Destination


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

    def tosId(self, fields=None):
        hotel = Hotel.objects.filter(sourceId=self._hotelUpdate.sourceId,
                                     source=self._hotelUpdate.source).first()
        if hotel and hotel.tosId:
            return djangoUtils.encodeId(hotel.tosId)
        else:
            return None

    def countryId(self, fields=None):
        hotel = Hotel.objects.filter(sourceId=self._hotelUpdate.sourceId,
                                     source=self._hotelUpdate.source).first()
        destination = Destination.objects.filter(sourceId=hotel.cityId, source=hotel.source).first()
        if not destination:
            return None

        destination = Destination.objects.filter(countryCode=destination.countryCode,
                                                 sourceId__isnull=True,
                                                 source=hotel.source).first()
        if not destination:
            return None
        return destination.tosId

    def cityId(self, fields=None):
        hotel = Hotel.objects.filter(sourceId=self._hotelUpdate.sourceId,
                                     source=self._hotelUpdate.source).first()
        destination = Destination.objects.filter(sourceId=hotel.cityId, source=hotel.source).first()
        if not destination:
            return None
        return destination.tosId
