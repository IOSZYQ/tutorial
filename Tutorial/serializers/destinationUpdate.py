__author__ = 'HanHui'

import projectConfig

from django.utils import timezone

from utilities import DataSerializer, djangoUtils

from ..models import DestinationUpdate, Destination
from ..dataFormat.destination import DestinationFields
from .destination import DestinationSerializer


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

    def destination(self, fields=None):
        if fields == True:
            return djangoUtils.encodeId(self._destinationUpdate.destination_id)
        return DestinationSerializer(destination=destination, fields=DestinationFields.brief).data
