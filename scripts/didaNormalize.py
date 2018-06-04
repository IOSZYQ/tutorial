__author__ = 'HanHui'

import os
import sys
import time
import json
import django
import argparse
import collections

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tutorial_Server.settings")
django.setup()

from django.conf import settings
from clients.map import GoogleMapClient
from utilities.utils import generateVersion
from Tutorial.models import Destination, Dida, DestinationUpdate, DestinationSubCity, Hotel, HotelUpdate


def _generateCountryUpdate(destination, data, newVersion):
    name_cn = data["name_cn"]
    name_en = data["name_en"]

    if not destination:
        return data
    elif destination.version != newVersion:
        update = {}
        if name_cn != destination.name_cn:
            update.update({"name_cn": name_cn})
        if name_en != destination.name_en:
            update.update({"name_en": name_en})
        return update
    else:
        return None


def _generateCityUpdate(destination, data, newVersion):
    name_cn = data["name_cn"]
    name_en = data["name_en"]

    if not destination:
        return dict(data)
    elif destination.version != newVersion:
        update = {}
        if name_cn != destination.name_cn:
            update.update({"name_cn": name_cn})
        if name_en != destination.name_en:
            update.update({"name_en": name_en})
        return update
    else:
        return None


def _generateHotelUpdate(hotel, data, newVersion):
    name_cn = data["name_cn"]
    name_en = data["name_en"]
    address = data["address"]
    cityId = data["cityId"]
    zipCode = data["zipCode"]
    longitude = data["longitude"]
    latitude = data["latitude"]
    starRating = data["starRating"]
    telephone = data["telephone"]

    if not hotel:
        return dict(data)
    elif hotel.version != newVersion:
        update = {}
        if name_cn != hotel.name_cn:
            update.update({"name_cn": name_cn})
        if name_en != hotel.name_en:
            update.update({"name_en": name_en})
        if address != hotel.address:
            update.update({"address": address})
        if cityId != hotel.cityId:
            update.update({"cityId": cityId})
        if zipCode != hotel.zipCode:
            update.update({"zipCode": zipCode})
        if longitude != hotel.longitude:
            update.update({"longitude": longitude})
        if latitude != hotel.latitude:
            update.update({"latitude": latitude})
        if starRating != hotel.starRating:
            update.update({"starRating": starRating})
        if telephone != hotel.telephone:
            update.update({"telephone": telephone})
        return update
    else:
        return None


def normalizeDidaCountry():
    dida = Dida.objects.filter(normalizeTime__isnull=True).order_by("-created").first()
    filePath = os.path.join(settings.STATICFILES_DIRS[0], "dida", dida.countryFile)
    countryFile = open(filePath, "r")
    countries = json.loads(countryFile.read())

    for countryInfo in countries:
        name_cn = countryInfo["CountryName_CN"]
        name_en = countryInfo["CountryName"]
        countryCode = countryInfo["ISOCountryCode"]

        data = collections.OrderedDict([("name_cn", name_cn), ("name_en", name_en), ("countryCode", countryCode)])
        newVersion = generateVersion(data)

        destination = Destination.objects.filter(countryCode=countryCode, source="dida").first()
        update = _generateCountryUpdate(destination, data, newVersion)

        if update:
            destinationUpdate = DestinationUpdate.objects.filter(countryCode=countryCode).first()
            if not destinationUpdate:
                DestinationUpdate.objects.create(countryCode=countryCode, source="dida", json=json.dumps(update))
            else:
                destinationUpdate.data = json.dumps(update)
                destinationUpdate.save()


def normalizeDidaCity():
    dida = Dida.objects.filter(normalizeTime__isnull=True).order_by("-created").first()
    filePath = os.path.join(settings.STATICFILES_DIRS[0], "dida", dida.cityFile)
    cityFile = open(filePath, "r")
    cities = json.loads(cityFile.read())

    subCityMap = {}
    for city in cities:
        sourceId = city["CityCode"]
        parentCityCode = city["ParentCityCode"] if "ParentCityCode" in city else None
        if parentCityCode != sourceId:
            subCityMap.setdefault(parentCityCode, []).append(sourceId)

    for city in cities:
        name_en = city["CityName"]
        name_cn = city["CityName_CN"] if "CityName_CN" in city else None
        sourceId = city["CityCode"]
        parentCityCode = city["ParentCityCode"] if "ParentCityCode" in city else None
        if parentCityCode != sourceId:
            continue
        countryCode = city["CountryCode"]
        data = collections.OrderedDict([("name_cn", name_cn),
                                        ("name_en", name_en)])
        newVersion = generateVersion(data)

        destination = Destination.objects.filter(sourceId=sourceId, source="dida").first()
        update = _generateCityUpdate(destination, data, newVersion)

        if update:
            destinationUpdate = DestinationUpdate.objects.filter(sourceId=sourceId).first()
            if not destinationUpdate:
                destinationUpdate = DestinationUpdate.objects.create(sourceId=sourceId, countryCode=countryCode, source="dida", json=json.dumps(update))
                subCities = []
                if sourceId in subCityMap:
                    for subCityCode in subCityMap[sourceId]:
                        subCities.append(DestinationSubCity(update=destinationUpdate, cityId=subCityCode))
                if subCities:
                    DestinationSubCity.objects.bulk_create(subCities)
            else:
                destinationUpdate.data = json.dumps(update)
                destinationUpdate.save()


def normalizeDidaHotel():
    dida = Dida.objects.filter(normalizeTime__isnull=True).order_by("-created").first()
    filePath = os.path.join(settings.STATICFILES_DIRS[0], "dida", dida.hotelFile)
    hotelFile = open(filePath, "r", encoding="utf-8")
    hotels = hotelFile.read()

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

        data = collections.OrderedDict([("name_cn", name_cn),
                                        ("name_en", name_en),
                                        ("address", address),
                                        ("cityId", cityId),
                                        ("zipCode", zipCode),
                                        ("longitude", longitude),
                                        ("latitude", latitude),
                                        ("starRating", starRating),
                                        ("telephone", telephone)])
        newVersion = generateVersion(data)

        hotel = Hotel.objects.filter(sourceId=sourceId, source="dida").first()
        update = _generateHotelUpdate(hotel, data, newVersion)

        if update:
            hotelUpdate = HotelUpdate.objects.filter(source="dida", sourceId=sourceId).first()
            if not hotelUpdate:
                HotelUpdate.objects.create(sourceId=sourceId, longitude=longitude, latitude=latitude, cityId=cityId, source="dida", json=json.dumps(update))
            else:
                hotelUpdate.data = json.dumps(update)
                hotelUpdate.save()


def gecodeLocationWithHotelInfo():
    destinationUpdates = DestinationUpdate.objects.filter(longitude__isnull=True,
                                                          latitude__isnull=True,
                                                          sourceId__isnull=False).order_by("id")
    for destinationUpdate in destinationUpdates:
        print(destinationUpdate.id)
        cityIds = DestinationSubCity.objects.filter(update=destinationUpdate).values_list("cityId", flat=True)

        cityIds = list(cityIds)
        cityIds.append(destinationUpdate.sourceId)
        hotel = HotelUpdate.objects.filter(cityId__in=cityIds, source="dida").first()
        if not hotel:
            continue

        destinationUpdate.longitude = hotel.longitude
        destinationUpdate.latitude = hotel.latitude
        destinationUpdate.save()


def geocodeLocationWithMapApi():
    count = 0
    destinationUpdates = DestinationUpdate.objects.filter(longitude__isnull=True,
                                                          latitude__isnull=True,
                                                          source="dida").order_by("id")

    client = GoogleMapClient()
    for destinationUpdate in destinationUpdates:
        print(destinationUpdate.id)
        jsonData = json.loads(destinationUpdate.json)
        longitude, latitude = client.searchLocation(jsonData["name_en"])
        if longitude and latitude:
            destinationUpdate.longitude = longitude
            destinationUpdate.latitude = latitude
            destinationUpdate.save()
        count += 1
        if count >= 2500:
            break
        time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument("--country", action="store_true", help="normalize countries")
    parser.add_argument("--city", action="store_true", help="normalize cities")
    parser.add_argument("--hotel", action="store_true", help="normalize hotels")
    parser.add_argument("--gecode1", action="store_true", help="gecode cities")
    parser.add_argument("--gecode2", action="store_true", help="gecode cities")

    args = parser.parse_args()
    if args.country:
        normalizeDidaCountry()
    if args.city:
        normalizeDidaCity()
    if args.hotel:
        normalizeDidaHotel()
    if args.gecode1:
        gecodeLocationWithHotelInfo()
    if args.gecode2:
        geocodeLocationWithMapApi()
