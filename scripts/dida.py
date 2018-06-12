__author__ = 'HanHui'

import os
import sys
import time
import json
import django
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tutorial_Server.settings")
django.setup()

import datetime
import projectConfig

from django.conf import settings
from clients import GoogleMapClient, DidaClient
from utilities.utils import generateVersion
from Tutorial.models import Destination, Dida, DestinationUpdate, Hotel, HotelUpdate


def _saveStaticData(dateStr, countryJson=None, cityJson=None, hotelCsv=None):
    fileName = None
    data = None

    if countryJson:
        fileName = "country_{0}.json".format(dateStr)
        data = countryJson

    if cityJson:
        fileName = "city_{0}.json".format(dateStr)
        data = cityJson

    if hotelCsv:
        fileName = "hotel{0}.csv".format(dateStr)
        data = hotelCsv

    if fileName and data:
        filePath = os.path.join(settings.STATICFILES_DIRS[0], "dida", fileName)
        saveFile = open(filePath, "w", encoding="utf-8", newline="")
        saveFile.write(data)
        saveFile.close()
    return fileName


def downloadDidaStaticData():
    dateStr = datetime.datetime.now().strftime(projectConfig.DATETIME_FILE_FORMAT)
    client = DidaClient()
    countries = client.downCountryList()["Countries"]

    countryJson = json.dumps(countries, indent=4)
    countryFile = _saveStaticData(dateStr, countryJson=countryJson)

    cityList = []
    countryCodes = [country["ISOCountryCode"] for country in countries]
    for countryCode in countryCodes:
        cities = client.downCityList(countryCode=countryCode)
        if not cities or "Cities" not in cities:
            continue

        cityList.extend(cities["Cities"])
    cityJson = json.dumps(cityList, indent=4)
    cityFile = _saveStaticData(dateStr, cityJson=cityJson)

    hotelCsv = client.downGetStaticInformation()
    hotelFile = _saveStaticData(dateStr, hotelCsv=hotelCsv)

    Dida.objects.create(countryFile=countryFile, cityFile=cityFile, hotelFile=hotelFile)


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


def _generateHotelUpdate(hotel, data, newVersion):
    name_cn = data["name_cn"]
    name_en = data["name_en"]
    address = data["address"]
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
    dida = Dida.objects.filter().order_by("-created").first()
    filePath = os.path.join(settings.STATICFILES_DIRS[0], "dida", dida.countryFile)
    countryFile = open(filePath, "r")
    countries = json.loads(countryFile.read())

    for countryInfo in countries:
        name_cn = countryInfo["CountryName_CN"]
        name_en = countryInfo["CountryName"]
        countryCode = countryInfo["ISOCountryCode"]

        data = [("name_cn", name_cn), ("name_en", name_en)]
        newVersion = generateVersion(data)

        destination = Destination.objects.filter(countryCode=countryCode,
                                                 source="dida",
                                                 sourceId__isnull=True).first()
        update = _generateCountryUpdate(destination, dict(data), newVersion)

        newDestinationUpdates = []
        if update:
            destinationUpdate = DestinationUpdate.objects.filter(countryCode=countryCode,
                                                                 source="dida",
                                                                 sourceId__isnull=True).first()
            if not destinationUpdate:
                newDestinationUpdates.append(DestinationUpdate(countryCode=countryCode, source="dida", json=json.dumps(update)))
            else:
                destinationUpdate.data = json.dumps(update)
                destinationUpdate.save()
        if newDestinationUpdates:
            DestinationUpdate.objects.bulk_create(newDestinationUpdates)


def normalizeDidaCity():
    dida = Dida.objects.filter().order_by("-created").first()
    filePath = os.path.join(settings.STATICFILES_DIRS[0], "dida", dida.cityFile)
    cityFile = open(filePath, "r")
    cities = json.loads(cityFile.read())

    cityMap = {}
    for city in cities:
        sourceId = city["CityCode"]
        parentCityCode = city["ParentCityCode"] if "ParentCityCode" in city else None
        countryCode = city["CountryCode"]

        if countryCode not in cityMap:
            cityMap[countryCode] = {}

        if parentCityCode != sourceId:
            if parentCityCode not in cityMap[countryCode]:
                cityMap[countryCode][parentCityCode] = {"subCityList": []}

            cityMap[countryCode][parentCityCode]["subCityList"].append(sourceId)
        else:
            if sourceId not in cityMap[countryCode]:
                cityMap[countryCode][sourceId] = {"subCityList": [sourceId], "info": city}
            else:
                cityMap[countryCode][sourceId]["info"] = city

    for cities in cityMap.values():
        for city in cities.values():
            if "info" not in city or "subCityList" not in city:
                continue

            cityInfo = city["info"]
            subCityList = json.dumps(city["subCityList"])
            name_en = cityInfo["CityName"]
            name_cn = cityInfo["CityName_CN"] if "CityName_CN" in cityInfo else None
            sourceId = cityInfo["CityCode"]
            countryCode = cityInfo["CountryCode"]

            data = [("name_cn", name_cn), ("name_en", name_en)]
            newVersion = generateVersion(data)

            destination = Destination.objects.filter(sourceId=sourceId, source="dida").first()
            update = _generateCityUpdate(destination, dict(data), newVersion)

            newDestinationUpdates = []
            if update:
                destinationUpdate = DestinationUpdate.objects.filter(sourceId=sourceId, source="dida").first()
                if not destinationUpdate:
                    newDestinationUpdates.append(DestinationUpdate(sourceId=sourceId, subCities=subCityList, countryCode=countryCode, source="dida", json=json.dumps(update)))
                else:
                    destinationUpdate.data = json.dumps(update)
                    destinationUpdate.save()
            if newDestinationUpdates:
                DestinationUpdate.objects.bulk_create(newDestinationUpdates)


def normalizeDidaHotel():
    dida = Dida.objects.filter().order_by("-created").first()
    filePath = os.path.join(settings.STATICFILES_DIRS[0], "dida", dida.hotelFile)
    hotelFile = open(filePath, "r", encoding="utf-8")
    hotels = hotelFile.read()

    newHotelUpdates = []
    for hotelInfo in hotels.split("\n")[1:]:
        items = hotelInfo.split("|")
        if len(items) < 16:
            continue

        sourceId = items[0]
        name_en = items[1]
        name_cn = items[2]
        address = items[3]
        cityId = items[4]
        countryCode = items[8]
        zipCode = items[11]
        longitude = float(items[12]) if items[12] else None
        latitude = float(items[13]) if items[13] else None
        if latitude and longitude and latitude > 90:
            tmp = longitude
            longitude = latitude
            latitude = tmp
        starRating = items[14]
        telephone = items[15]

        data = [("name_cn", name_cn),
                ("name_en", name_en),
                ("address", address),
                ("zipCode", zipCode),
                ("longitude", longitude),
                ("latitude", latitude),
                ("starRating", starRating),
                ("telephone", telephone)]
        newVersion = generateVersion(data)

        hotel = Hotel.objects.filter(sourceId=sourceId, source="dida").first()
        update = _generateHotelUpdate(hotel, dict(data), newVersion)

        if update:
            hotelUpdate = HotelUpdate.objects.filter(source="dida", sourceId=sourceId).first()
            if not hotelUpdate:
                newHotelUpdates.append(
                    HotelUpdate(sourceId=sourceId,
                                countryCode=countryCode,
                                longitude=longitude,
                                latitude=latitude,
                                cityId=cityId,
                                source="dida",
                                json=json.dumps(update))
                )
            else:
                hotelUpdate.data = json.dumps(update)
                hotelUpdate.save()
        if len(newHotelUpdates) >= 128:
            HotelUpdate.objects.bulk_create(newHotelUpdates)
            newHotelUpdates = []


def gecodeLocationWithHotelInfo():
    destinationUpdates = DestinationUpdate.objects.filter(longitude__isnull=True,
                                                          latitude__isnull=True,
                                                          sourceId__isnull=False).order_by("id")
    for destinationUpdate in destinationUpdates:
        cityIds = json.loads(destinationUpdate.subCities)
        hotelUpdate = HotelUpdate.objects.filter(cityId__in=cityIds, source="dida").first()
        if not hotelUpdate:
            continue

        destinationUpdate.longitude = hotelUpdate.longitude
        destinationUpdate.latitude = hotelUpdate.latitude
        destinationUpdate.save()


def geocodeLocationWithMapApi():
    count = 0
    destinationUpdates = DestinationUpdate.objects.filter(longitude__isnull=True,
                                                          latitude__isnull=True,
                                                          source="dida").order_by("id")

    client = GoogleMapClient()
    for destinationUpdate in destinationUpdates:
        jsonData = json.loads(destinationUpdate.json)
        longitude, latitude = client.searchLocation(jsonData["name_en"], destinationUpdate.countryCode)
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
    parser.add_argument("--download", action="store_true", help="download dida data")
    parser.add_argument("--country", action="store_true", help="normalize countries")
    parser.add_argument("--city", action="store_true", help="normalize cities")
    parser.add_argument("--hotel", action="store_true", help="normalize hotels")
    parser.add_argument("--gecode1", action="store_true", help="gecode cities")
    parser.add_argument("--gecode2", action="store_true", help="gecode cities")

    args = parser.parse_args()
    if args.download:
        downloadDidaStaticData()
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
