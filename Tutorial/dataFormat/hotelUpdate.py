__author__ = "HanHui"

from utilities import classproperty


class HotelUpdateFields:
    @classproperty
    def brief(cls):
        return {
            "id"            : True,
            "sourceId"      : True,
            "json"          : True,
            "updated"       : True,
            "created"       : True
        }
