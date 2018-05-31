__author__ = 'HanHui'

import projectConfig

from django.utils import timezone

from utilities import DataSerializer, djangoUtils

from ..models import DestinationUpdate, Destination


class DestinationUpdateSerializer(DataSerializer):
    def __init__(self, destinationUpdate, fields, parameters=None):
        if isinstance(destinationUpdate, int) or isinstance(destinationUpdate, str):
            destinationUpdate = DestinationUpdate.objects.get(pk=destinationUpdate)

        super(DestinationUpdateSerializer, self).__init__(destinationUpdate, fields, parameters)

        self._destinationUpdate = destinationUpdate

    def created(self, fields=None):
        return timezone.localtime(self._destinationUpdate.created).strftime(projectConfig.DATE_TIME_FORMAT)

    def updated(self, fields=None):
        return timezone.localtime(self._destinationUpdate.updated).strftime(projectConfig.DATE_TIME_FORMAT)

    def parentId(self, fields=None):
        if not self._destinationUpdate.sourceId:
            return None

        destination = Destination.objects.filter(sourceId__isnull=True,
                                                 source = self._destinationUpdate.source,
                                                 countryCode=self._destinationUpdate.countryCode).first()
        return djangoUtils.encodeId(destination.tosId)

    def tosId(self, fields=None):
        destination = Destination.objects.filter(sourceId=self._destinationUpdate.sourceId,
                                                 source=self._destinationUpdate.source,
                                                 countryCode=self._destinationUpdate.countryCode).first()
        if destination and destination.tosId:
            return djangoUtils.encodeId(destination.tosId)
        else:
            return None
