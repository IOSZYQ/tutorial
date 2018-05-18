# _*_ coding: utf-8 _*_
__author__ = 'alan'
__date__ = '2018/4/28 下午2:56'

import os

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tutorial.settings")

    import django, datetime
    from itertools import groupby, chain
    django.setup()


    from Hotel_Supplier.views import *

    from Hotel_Supplier.models import *

    sync = SyncDida()
    # countys = sync.downCountryList()
    # newCountrys = []
    # for county in countys['Countries']:
    #     newCountrys.append(DidaCountry(sourceId=county['ISOCountryCode'],name_cn=county['CountryName_CN'],name_en=county['CountryName']))
    # DidaCountry.objects.bulk_create(newCountrys)
    # print(countys)

    countrys = DidaCountry.objects.all()
    for rawCountry in countrys:
        country = DidaCountry.objects.get(sourceId=rawCountry.sourceId)
        citys = sync.downCityList(countryCode=rawCountry.sourceId)
        newCitys = []
        oldCitys = []
        print(rawCountry.name_cn,citys)
        if 'Cities' in citys:
            for rawCity in citys['Cities']:
                city = DidaCity.objects.filter(sourceId=rawCity["CityCode"]).first()
                if city:
                    city.country = country
                    city.name_cn = rawCity['CityName_CN']
                    city.name_en = rawCity['CityName']
                    oldCitys.append(city)
                else:
                    newCitys.append(DidaCity(country=country,name_cn=rawCity["CityName_CN"], sourceId=rawCity['CityCode'],name_en=rawCity['CityName']))
        DidaCity.objects.bulk_create(newCitys)