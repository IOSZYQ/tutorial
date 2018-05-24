__author__ = "HanHui"

from utilities import classproperty


class DestinationUpdateFields:
    @classproperty
    def brief(cls):
        return {
            "id"            : True,
            "sourceId"      : True,
            "countryCode"   : True,
            "json"          : True,
            "updated"       : True,
            "created"       : True
        }
