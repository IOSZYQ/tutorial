__author__ = "HanHui"

from utilities import classproperty


class DestinationFields:
    @classproperty
    def brief(cls):
        return {
            "id"             : True,
            "source"         : True,
            "sourceId"       : True,
            "parentId"       : True,
            "countryCode"    : True,
            "tosId"          : True,
            "updated"        : True,
            "created"        : True,
            "longitude"      : True,
            "latitude"       : True
        }
