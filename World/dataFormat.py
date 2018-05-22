__author__ = 'swolfod'

from utilities import classproperty

class DestinationFields:
    @classproperty
    def brief(cls):
        return {
            "id"		: True, #str
            "name_en"	: True,	#str
            "name_cn"	: True,	#str
            "coverPic"	: True, #imageurl 封面图片
            "countryFlag": True, #imageurl 国旗
            "type"		: True, #int 目的地类型，0－洲，1-国家，2-城市
            "latitude"  : True,	#float
            "longitude" : True,	#float
            "weight"    : True, #int
            "bounds"    : {     #bounds 目的地区域矩形边框
                "latitudeN"     : True,
                "latitudeS"     : True,
                "longitudeE"    : True,
                "longitudeW"    : True
            },
            "parent": {
                "id"		: True, #str
                "name_en"	: True,	#str
                "name_cn"	: True,	#str
            },
            "timeStamp" : True
        }


    @classproperty
    def full(cls):
        fields = cls.brief

        fields.update({
            "parent"        : cls.brief,
            "introduction"  : True,
            "infos"         : True,
            "defaultCard"   : True,
            "visaInfo"      : True,
            "inactive"      : True
        })

        return fields


    @classproperty
    def recommendedCities(cls):
        return {
            "recommendedCities": {
                "majorCities"   : cls.brief,
                "cities"        : cls.brief
            }
        }


    @classproperty
    def subCountries(cls):
        return {
            "subCountries": {
                "countries"         : cls.brief,
                "popularCountries"  : True,
                "majorCountries"      : True
            }
        }


    @classproperty
    def allFields(cls):
        fields = cls.full
        fields.update(cls.recommendedCities)
        fields.update(cls.subCountries)
        fields["inactive"] = True
        fields["weight"] = True
        fields["aliases"] = True
        fields["public"] = True
        fields["parent"] = cls.full
        fields["parent"]["weight"] = True
        fields["parent"]["public"] = True
        return fields
