__author__ = 'HanHui'

import projectConfig

from django.utils import timezone

from utilities import DataSerializer, djangoUtils

from ..models import Destination


class DestinationSerializer(DataSerializer):
    def __init__(self, destination, fields, parameters=None):
        if isinstance(destination, int) or isinstance(destination, str):
            destination = Destination.objects.get(pk=destination)

        super(DestinationSerializer, self).__init__(destination, fields, parameters)

        self._destination = destination

    def created(self, fields=None):
        return timezone.localtime(self._destination.created).strftime(projectConfig.DATE_TIME_FORMAT)

    def updated(self, fields=None):
        return timezone.localtime(self._destination.updated).strftime(projectConfig.DATE_TIME_FORMAT)

    def parentId(self, fields=None):
        if self._destination.parent and self._destination.parent.tosId:
            return djangoUtils.encodeId(self._destination.parent.tosId)
        else:
            return None

    def countryCode(self, fields=None):
        if self._destination.parent and self._destination.parent.tosId:
            return self._destination.parent.sourceId
        else:
            return self._destination.sourceId

    def tosId(self, fields=None):
        if self._destination.tosId:
            return djangoUtils.encodeId(self._destination.tosId)
        else:
            return None
