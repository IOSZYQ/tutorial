__author__ = 'HanHui'

import os
import sys
import json
import django
import collections

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tutorial_Server.settings")
django.setup()

from django.conf import settings
from clients.map import GoogleMapClient
from utilities.utils import generateVersion
from Tutorial.models import Destination, Dida, DestinationUpdate, Hotel, HotelUpdate


def _generateCountryUpdate(destination, data, newVersion):
    name_cn = data["name_cn"]
    name_en = data["name_en"]
    countryCode = data["countryCode"]

    if not destination:
        return data
    elif destination.version != newVersion:
        update = {}
        if name_cn != destination.name_cn:
            update.update({"name_cn": name_cn})
        if name_en != destination.name_en:
            update.update({"name_en": name_en})
        if countryCode != destination.countryCode:
            update.update({"countryCode": countryCode})
        return update
    else:
        return None


def _generateCityUpdate(destination, data, newVersion):
    name_cn = data["name_cn"]
    name_en = data["name_en"]
    countryCode = data["countryCode"]
    parentId = data["parentId"]
    sourceId = data["sourceId"]

    if not destination:
        return dict(data)
    elif destination.version != newVersion:
        update = {}
        if name_cn != destination.name_cn:
            update.update({"name_cn": name_cn})
        if name_en != destination.name_en:
            update.update({"name_en": name_en})
        if countryCode != destination.countryCode:
            update.update({"countryCode": countryCode})
        if parentId != destination.parentId:
            update.update({"parentId": parentId})
        if sourceId != destination.sourceId:
            update.update({"sourceId": sourceId})
        return update
    else:
        return None


def _generateHotelUpdate(hotel, data, newVersion):
    name_cn = data["name_cn"]
    name_en = data["name_en"]
    sourceId = data["sourceId"]
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
        if sourceId != hotel.sourceId:
            update.update({"sourceId": sourceId})
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

    for city in cities:
        name_en = city["CityName"]
        name_cn = city["CityName_CN"] if "CityName_CN" in city else None
        sourceId = city["CityCode"]
        parentId = city["ParentCityCode"] if "ParentCityCode" in city else None
        countryCode = city["CountryCode"]
        data = collections.OrderedDict([("name_cn", name_cn),
                                        ("name_en", name_en),
                                        ("countryCode", countryCode),
                                        ("sourceId", sourceId),
                                        ("parentId", parentId)])
        newVersion = generateVersion(data)

        destination = Destination.objects.filter(sourceId=sourceId, source="dida").first()
        update = _generateCityUpdate(destination, data, newVersion)

        if update:
            destinationUpdate = DestinationUpdate.objects.filter(sourceId=sourceId).first()
            if not destinationUpdate:
                DestinationUpdate.objects.create(sourceId=sourceId, countryCode=countryCode, source="dida", json=json.dumps(update))
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
                                        ("sourceId", sourceId),
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
            hotelUpdate = HotelUpdate.objects.filter(sourceId=sourceId).first()
            if not hotelUpdate:
                HotelUpdate.objects.create(sourceId=sourceId, source="dida", json=json.dumps(update))
            else:
                hotelUpdate.data = json.dumps(update)
                hotelUpdate.save()


def geocodeCountryLocation():
    countries = DestinationUpdate.objects.filter(sourceId__isnull=True).order_by("id")
    client = GoogleMapClient()

    for country in countries:
        address = country.name_en
        longitude, latitude = client.searchLocation(address)
        if longitude and latitude:
            country.longitude = longitude
            country.latitude = latitude
            country.save()


def geocodeCityLocation():
    cities = DestinationUpdate.objects.filter(sourceId__isnull=False).order_by("id")
    client = GoogleMapClient()

    for city in cities:
        address = city.name_en
        longitude, latitude = client.searchLocation(address)
        if longitude and latitude:
            city.longitude = longitude
            city.latitude = latitude
            city.save()

if __name__ == "__main__":
    normalizeDidaCountry()
    normalizeDidaCity()
    normalizeDidaHotel()

    geocodeCountryLocation()
    geocodeCityLocation()
