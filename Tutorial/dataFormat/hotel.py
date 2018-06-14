__author__ = "HanHui"

from utilities import classproperty
from .destination import DestinationFields


class HotelFields:
    @classproperty
    def brief(cls):
        return {
            "id"            : True,
            "source"        : True,
            "sourceId"      : True,
            "tosId"         : True,
            "destination"   : DestinationFields.brief,
            "updated"       : True,
            "created"       : True,
        }
