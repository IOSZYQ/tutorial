__author__ = 'HanHui'

import os
import sys
import json
import django
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tutorial_Server.settings")
django.setup()

import projectConfig
from utilities import djangoUtils

from clients import DidaClient, GoogleMapClient
from Tutorial.models.dida import (DidaCountry, DidaCity, DidaBedType, DidaBreakfastType, DidaHotel)

COUNTRIES_MAP = {
    "AE": 16,
    "AS": 192,
    "AX": 190,
    "BL": 195,
    "CD": 46,
    "CF": 39,
    "CG": 47,
    "CI": 44,
    "CK": 198,
    "CW": 201,
    "DM": 57,
    "DO": 203,
    "EU": 4,
    "FK": 67,
    "FM": 205,
    "FO": 204,
    "GN": 73,
    "GQ": 76,
    "GW": 75,
    "HM": 210,
    "KN": 215,
    "KR": 100,
    "KY": 202,
    "LC": 216,
    "MD": 112,
    "MF": 219,
    "MH": 222,
    "NC": 125,
    "NF": 227,
    "NZ": 132,
    "PG": 138,
    "PM": 237,
    "SB": 154,
    "SD": 151,
    "SS": 152,
    "SY": 164,
    "TC": 241,
    "TZ": 175,
    "VA": 243,
    "VC": 244,
    "VG": 245,
    "WS": 248
}

COUNTRIES_NOT_FOUND = [
    "AN",
    "BQ",
    "BV",
    "CC",
    "CX",
    "EU",
    "FW",
    "GF",
    "GP",
    "GS",
    "GU",
    "IO",
    "KV",
    "MQ",
    "MP",
    "PS",
    "SJ",
    "TK",
    "UM",
    "VI",
    "YT"
]


def syncDidaCountry():
    client = DidaClient()
    countries = client.downCountryList()["Countries"]
    if not countries:
        return

    for countryInfo in countries:
        name_cn = countryInfo["CountryName_CN"]
        name_en = countryInfo["CountryName"]
        sourceId = countryInfo["ISOCountryCode"]
        country, created = DidaCountry.objects.get_or_create(sourceId=sourceId,
                                                            defaults={
                                                                "name_cn": name_cn,
                                                                "name_en": name_en
                                                            })
        if not created:
            country.name_cn = name_cn
            country.name_en = name_en
            country.save()


def syncDidaCity():
    client = DidaClient()

    countries = DidaCountry.objects.filter(inactive=False).all()
    countries = {country.sourceId: country for country in countries}

    for countryCode in countries.keys():
        cities = client.downCityList(countryCode=countryCode)
        if not cities or "Cities" not in cities:
            continue

        for cityInfo in cities["Cities"]:
            name_en = cityInfo["CityName"]
            name_cn = cityInfo["CityName_CN"] if "CityName_CN" in cityInfo else None
            sourceId = cityInfo["CityCode"]
            parentId = cityInfo["ParentCityCode"] if "ParentCityCode" in cityInfo else None
            country = countries[countryCode]

            city, created = DidaCity.objects.get_or_create(sourceId=sourceId,
                                                           defaults={
                                                               "name_en": name_en,
                                                               "name_cn": name_cn,
                                                               "country": country,
                                                               "parentId": parentId
                                                           })

            if not created:
                city.name_en = name_en
                city.name_cn = name_cn
                city.country = country
                city.parentId = parentId
                city.save()


def syncDidaBedType():
    client = DidaClient()
    bedTypes = client.downBedTypeList()["BedTypes"]

    for bedTypeInfo in bedTypes:
        defaultOccupancy = bedTypeInfo["DefaultOccupancy"]
        typeId = bedTypeInfo["ID"]
        name_en = bedTypeInfo["Name"]
        name_cn = bedTypeInfo["Name_CN"]

        bedType, created = DidaBedType.objects.get_or_create(typeId=typeId,
                                                             defaults={
                                                                "name_cn": name_cn,
                                                                "name_en": name_en,
                                                                "defaultOccupancy": defaultOccupancy
                                                             })
        if not created:
            bedType.name_cn = name_cn
            bedType.name_en = name_en
            bedType.defaultOccupancy = defaultOccupancy
            bedType.save()


def syncDidaBreakfast():
    client = DidaClient()
    breakfastTypes = client.downBreakfastTypeList()["Breakfasts"]

    for breakfastInfo in breakfastTypes:
        typeId = breakfastInfo["ID"]
        name_en = breakfastInfo["Name"]
        name_cn = breakfastInfo["Name_CN"]

        breakfastType, created = DidaBreakfastType.objects.get_or_create(typeId=typeId,
                                                                         defaults={
                                                                            "name_cn": name_cn,
                                                                            "name_en": name_en
                                                                         })
        if not created:
            breakfastType.name_cn = name_cn
            breakfastType.name_en = name_en
            breakfastType.save()


def syncDidaHotel():
    client = DidaClient()
    hotels = client.downGetStaticInformation()

    cities = DidaCity.objects.filter(inactive=False)
    cities = {city.sourceId: city for city in cities}
    for hotelInfo in hotels.split("\n")[1:]:
        items = hotelInfo.split("|")
        if len(items) < 16:
            continue

        sourceId = items[0]
        name_en = items[1]
        name_cn = items[2]
        address = items[3]
        cityId = items[4]
        zipCode = items[11]
        longitude = float(items[12]) if items[12] else None
        latitude = float(items[13]) if items[13] else None
        if latitude and longitude and latitude > 90:
            tmp = longitude
            longitude = latitude
            latitude = tmp
        starRating = items[14]
        telephone = items[15]

        hotel, created = DidaHotel.objects.get_or_create(sourceId=sourceId,
                                                         defaults={
                                                             "name_en": name_en,
                                                             "name_cn": name_cn,
                                                             "address": address,
                                                             "zipCode": zipCode,
                                                             "longitude": longitude,
                                                             "latitude": latitude,
                                                             "starRating": starRating,
                                                             "telephone": telephone,
                                                             "city": cities[cityId]
                                                         })

        if not created:
            hotel.name_cn = name_cn
            hotel.name_en = name_en
            hotel.address = address
            hotel.zipCode = zipCode
            hotel.longitude = longitude
            hotel.latitude = latitude
            hotel.starRating = starRating
            hotel.telephone = telephone
            hotel.city = cities[cityId]
            hotel.save()


def _findDestination(destName, type=1):
    if not destName:
        return None

    r = requests.get(projectConfig.TOS_DESTINATION_URL + "?type={0}&q={1}".format(type, destName))
    if r.status_code != 200:
        return None

    try:
        result = json.loads(r.text)
        if "result" not in result or "destinations" not in result["result"]:
            return None

        destinations = result["result"]["destinations"]
        if len(destinations) != 1:
            return None

        return djangoUtils.decodeId(destinations[0]["id"])
    except:
        return None


def _findPoi(hotelName, longitude, latitude):
    if not hotelName:
        return None

    r = requests.get(projectConfig.TOS_HOTEL_URL + "?longitude={0}&latitude={1}&distance=100&q={2}".format(longitude, latitude, hotelName))
    if r.status_code != 200:
        sys.exit(-1)

    try:
        result = json.loads(r.text)
        if "result" not in result or "hotels" not in result["result"]:
            return None

        hotels = result["result"]["hotels"]
        if len(hotels) != 1:
            return None

        return djangoUtils.decodeId(hotels[0]["id"])
    except:
        return None


def syncCountryDestId():
    countries = DidaCountry.objects.filter(inactive=False)
    for country in countries:
        if country.sourceId in COUNTRIES_NOT_FOUND:
            continue
        if country.sourceId in COUNTRIES_MAP:
            country.destId = COUNTRIES_MAP[country.sourceId]
            country.save()
        else:
            destId = _findDestination(country.name_en, type=1)
            if not destId:
                destId = _findDestination(country.name_cn, type=1)
            if not destId:
                continue

            country.destId = destId
            country.save()


def syncCityDestId():
    count = 0
    cities = DidaCity.objects.filter(inactive=False)
    for city in cities:
        count = count + 1
        print(count, city.name_cn)
        destId = _findDestination(city.name_en, type=2)
        if not destId:
            destId = _findDestination(city.name_cn, type=2)
        if not destId:
            continue

        city.destId = destId
        city.save()


def syncHotelPoiId():
    hotels = DidaHotel.objects.filter(inactive=False)
    for hotel in hotels:
        longitude = hotel.longitude
        latitude = hotel.latitude
        if not longitude or not latitude:
            continue

        name = hotel.name_en
        poiId = _findPoi(name, longitude, latitude)
        if not poiId:
            continue

        hotel.poiId = poiId
        hotel.save()


def syncCityLocation():
    cities = DidaCity.objects.filter(inactive=False)
    client = GoogleMapClient()

    for city in cities:
        address = city.name_en
        longitude, latitude = client.searchLocation(address)
        city.longitude = longitude
        city.latitude = latitude
        city.save()

if __name__ == "__main__":
    # syncDidaCountry()
    # syncDidaCity()
    #syncDidaHotel()
    # syncCountryDestId()
    #syncCityDestId()
    #syncHotelPoiId()
    syncCityLocation()
