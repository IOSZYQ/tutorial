__author__ = "HanHui"

from utilities import classproperty


class HotelUpdateFields:
    @classproperty
    def brief(cls):
        return {
            "id"            : True,
            "source"        : True,
            "sourceId"      : True,
            "tosId"         : True,
            "json"          : True,
            "updated"       : True,
            "created"       : True
        }
