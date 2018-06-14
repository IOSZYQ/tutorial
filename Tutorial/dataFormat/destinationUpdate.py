__author__ = "HanHui"

from utilities import classproperty
from .destination import DestinationFields


class DestinationUpdateFields:
    @classproperty
    def brief(cls):
        return {
            "id"             : True,
            "json"           : True,
            "updated"        : True,
            "created"        : True,
            "destination"    : DestinationFields.brief
        }
