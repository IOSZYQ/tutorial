__author__ = "HanHui"

from utilities import classproperty
from .hotel import HotelFields


class HotelUpdateFields:
    @classproperty
    def brief(cls):
        return {
            "id"            : True,
            "hotel"         : HotelFields.brief,
            "json"          : True,
            "updated"       : True,
            "created"       : True,
        }
