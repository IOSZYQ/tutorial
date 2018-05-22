__author__ = 'HanHui'

import os
import sys
import json
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tutorial_Server.settings")
django.setup()

from Tutorial.models import Destination, Dida


def normalizeDidaCountry():
    dida = Dida.objects.filter(syncTime__isnull=True).order_by("-created").first()
    countryFilePath = dida.countryFilePath
    countryFile = open(countryFilePath, "r")
    countries = json.loads(countryFile.read())

    for countryInfo in countries:
        name_cn = countryInfo["CountryName_CN"]
        name_en = countryInfo["CountryName"]
        countryCode = countryInfo["ISOCountryCode"]
        country, created = Destination.objects.get_or_create(countryCode=countryCode,
                                                             source="dida",
                                                             defaults={
                                                                 "name_cn": name_cn,
                                                                 "name_en": name_en,
                                                                 "source": "dida",
                                                                 "countryCode": countryCode,
                                                                 "adminLevel": 1
                                                             })
        if not created:
            country.name_cn = name_cn
            country.name_en = name_en
            country.save()


def normalizeDidaCity():
    dida = Dida.objects.filter(syncTime__isnull=True).order_by("-created").first()
    cityFilePath = dida.cityFilePath
    cityFile = open(cityFilePath, "r")
    cities = json.loads(cityFile.read())

    for city in cities:
        name_en = city["CityName"]
        name_cn = city["CityName_CN"] if "CityName_CN" in city else None
        sourceId = city["CityCode"]
        parentId = city["ParentCityCode"] if "ParentCityCode" in city else None
        countryCode = city["CountryCode"]

        city, created = Destination.objects.get_or_create(sourceId=sourceId,
                                                          source="dida",
                                                          defaults={
                                                              "name_en": name_en,
                                                              "name_cn": name_cn,
                                                              "countryCode": countryCode,
                                                              "parentId": parentId,
                                                              "source": "dida",
                                                              "adminLevel": 2
                                                          })

        if not created:
            city.name_en = name_en
            city.name_cn = name_cn
            city.countryCode = countryCode
            city.parentId = parentId
            city.save()

#
# def normalizeDidaHotel():
#     client = DidaClient()
#     hotels = client.downGetStaticInformation()
#
#     for hotelInfo in hotels.split("\n")[1:]:
#         items = hotelInfo.split("|")
#         if len(items) < 16:
#             continue
#
#         sourceId = items[0]
#         name_en = items[1]
#         name_cn = items[2]
#         address = items[3]
#         cityId = items[4]
#         zipCode = items[11]
#         longitude = float(items[12]) if items[12] else None
#         latitude = float(items[13]) if items[13] else None
#         if latitude and longitude and latitude > 90:
#             tmp = longitude
#             longitude = latitude
#             latitude = tmp
#         starRating = items[14]
#         telephone = items[15]
#
#         hotel, created = Hotel.objects.get_or_create(sourceId=sourceId,
#                                                      source="dida",
#                                                      defaults={
#                                                          "name_en": name_en,
#                                                          "name_cn": name_cn,
#                                                          "address": address,
#                                                          "zipCode": zipCode,
#                                                          "longitude": longitude,
#                                                          "latitude": latitude,
#                                                          "starRating": starRating,
#                                                          "telephone": telephone,
#                                                          "cityId": cityId,
#                                                          "source": "dida"
#                                                      })
#
#         if not created:
#             hotel.name_cn = name_cn
#             hotel.name_en = name_en
#             hotel.address = address
#             hotel.zipCode = zipCode
#             hotel.longitude = longitude
#             hotel.latitude = latitude
#             hotel.starRating = starRating
#             hotel.telephone = telephone
#             hotel.city = cityId
#             hotel.save()
#
#
# def _findDestination(destName, type=1):
#     if not destName:
#         return None
#
#     r = requests.get(projectConfig.TOS_DESTINATION_FIND_URL + "?type={0}&q={1}".format(type, destName))
#     if r.status_code != 200:
#         return None
#
#     try:
#         result = json.loads(r.text)
#         if "result" not in result or "destinations" not in result["result"]:
#             return None
#
#         destinations = result["result"]["destinations"]
#         if len(destinations) != 1:
#             return None
#
#         return djangoUtils.decodeId(destinations[0]["id"])
#     except:
#         return None
#
#
# def _findPoi(hotelName, longitude, latitude):
#     if not hotelName:
#         return None
#
#     r = requests.get(projectConfig.TOS_HOTEL_FIND_URL + "?longitude={0}&latitude={1}&distance=100&q={2}".format(longitude, latitude, hotelName))
#     if r.status_code != 200:
#         sys.exit(-1)
#
#     try:
#         result = json.loads(r.text)
#         if "result" not in result or "hotels" not in result["result"]:
#             return None
#
#         hotels = result["result"]["hotels"]
#         if len(hotels) != 1:
#             return None
#
#         return djangoUtils.decodeId(hotels[0]["id"])
#     except:
#         return None
#
#
# def _createTOSCityDestination(countryId, city):
#     headers = {
#         "Authorization": "Token {0}".format(_login())
#     }
#
#     url = projectConfig.TOS_DESTINATION_NEW_URL.format(countryId)
#     r = requests.put(url, json=city, headers=headers)
#     if r.status_code != 200:
#         if r.status_code == 403 or r.status_code == 401:
#             headers = {
#                 "Authorization": "Token {0}".format(_login(force=True))
#             }
#             r = requests.put(url, json=city, headers=headers)
#             if r.status_code != 200:
#                 return None
#         else:
#             return None
#
#     result = json.loads(r.text)
#     return result["result"]["city"]["id"]
#
#
# def _createTOSHotel(hotel):
#     pass
#
#
# def associateCountrySourceIdwithTOSId():
#     countries = Country.objects.filter(inactive=False).order_by("id")
#     for country in countries:
#         if country.destId:
#             continue
#
#         if country.sourceId in COUNTRIES_NOT_FOUND:
#             continue
#
#         if country.sourceId in COUNTRIES_MAP:
#             country.destId = COUNTRIES_MAP[country.sourceId]
#             country.save()
#         else:
#             destId = _findDestination(country.name_en, type=1)
#             if not destId:
#                 destId = _findDestination(country.name_cn, type=1)
#
#             if destId:
#                 country.destId = destId
#                 country.save()
#
#
# def associateCitySourceIdwithTOSId():
#     cities = City.objects.filter(inactive=False).order_by("id")
#     for city in cities:
#         if city.destId:
#             continue
#
#         destId = _findDestination(city.name_en, type=2)
#         if not destId:
#             destId = _findDestination(city.name_cn, type=2)
#
#         if destId:
#             city.destId = destId
#             city.save()
#         else:
#             if not city.longitude or not city.latitude:
#                 continue
#
#             cityId = _createTOSCityDestination(djangoUtils.encodeId(city.country.destId), {
#                 "name": city.name_cn if city.name_cn else city.name_en,
#                 "name_cn": city.name_cn,
#                 "name_en": city.name_en,
#                 "longitude": city.longitude,
#                 "latitude": city.latitude
#             })
#             if cityId:
#                 city.destId = djangoUtils.decodeId(cityId)
#                 city.save()
#
#
# def associateHotelSourceIdwithTOSId():
#     hotels = Hotel.objects.filter(inactive=False).order_by("id")
#     for hotel in hotels:
#         if hotel.poiId:
#             continue
#
#         longitude = hotel.longitude
#         latitude = hotel.latitude
#         if not longitude or not latitude:
#             continue
#
#         name = hotel.name_en
#         poiId = _findPoi(name, longitude, latitude)
#         if poiId:
#             hotel.poiId = poiId
#             hotel.save()
#         else:
#             _createTOSHotel(hotel)
#
#
# def geocodeCountryLocation():
#     countries = Country.objects.filter(inactive=False).order_by("id")
#     client = GoogleMapClient()
#
#     for country in countries:
#         address = country.name_en
#         longitude, latitude = client.searchLocation(address)
#         if longitude and latitude:
#             country.longitude = longitude
#             country.latitude = latitude
#             country.save()
#
#
# def geocodeCityLocation():
#     cities = City.objects.filter(inactive=False).order_by("id")
#     client = GoogleMapClient()
#
#     for city in cities:
#         address = city.name_en
#         longitude, latitude = client.searchLocation(address)
#         if longitude and latitude:
#             city.longitude = longitude
#             city.latitude = latitude
#             city.save()

if __name__ == "__main__":
    normalizeDidaCountry()
    normalizeDidaCity()