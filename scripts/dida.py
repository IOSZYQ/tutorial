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
from utilities.utils import generateVersion, calculateCenterPos
from Tutorial.models import Destination, Dida, DestinationUpdate, DestinationSubCity, Hotel, HotelUpdate


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

    countryMap = {}
    for countryInfo in countries:
        name_cn = countryInfo["CountryName_CN"]
        name_en = countryInfo["CountryName"]
        sourceId = countryInfo["ISOCountryCode"]

        data = [("name_cn", name_cn), ("name_en", name_en)]
        countryMap[sourceId] = data

    destinations = Destination.objects.filter(sourceId__in=countryMap.keys(), source="dida")
    destinationExists = {destination.sourceId:destination for destination in destinations}

    jsonDataMap = {}
    newDestinations = []
    for sourceId, data in countryMap.items():
        newVersion = generateVersion(data)
        destination = destinationExists[sourceId] if sourceId in destinationExists else None
        update = _generateCountryUpdate(destination, dict(data), newVersion)
        if sourceId in destinationExists:
            if update:
                DestinationUpdate.objects.filter(destination=destinationExists[destination.sourceId]).update(json=json.dumps(update))
        else:
            newDestinations.append(Destination(sourceId=sourceId, source="dida"))
            jsonDataMap[sourceId] = json.dumps(update)

    if newDestinations:
        Destination.objects.bulk_create(newDestinations)
        destinations = Destination.objects.filter(source="dida", sourceId__in=jsonDataMap.keys())
        destinations = {destination.sourceId: destination for destination in destinations}

        newDestinationUpdates = []
        for sourceId, jsonData in jsonDataMap.items():
            destinationUpdate = DestinationUpdate(destination=destinations[sourceId], json=jsonData)
            newDestinationUpdates.append(destinationUpdate)
        DestinationUpdate.objects.bulk_create(newDestinationUpdates)


def _getCityMap(cities):
    cityMap = {}
    for city in cities:
        sourceId = city["CityCode"]
        parentCityCode = city["ParentCityCode"] if "ParentCityCode" in city else None
        countryCode = city["CountryCode"]

        if countryCode not in cityMap:
            cityMap[countryCode] = {}

        if parentCityCode != sourceId:
            if parentCityCode == "180003":
                countryCode = "CH"
            if parentCityCode not in cityMap[countryCode]:
                cityMap[countryCode][parentCityCode] = {"subCities": [parentCityCode]}

            cityMap[countryCode][parentCityCode]["subCities"].append(sourceId)
        else:
            if sourceId not in cityMap[countryCode]:
                cityMap[countryCode][sourceId] = {"subCities": [sourceId], "info": city}
            else:
                cityMap[countryCode][sourceId]["info"] = city
    return cityMap


def normalizeDidaCity():
    dida = Dida.objects.filter().order_by("-created").first()
    filePath = os.path.join(settings.STATICFILES_DIRS[0], "dida", dida.cityFile)
    cityFile = open(filePath, "r")
    cities = json.loads(cityFile.read())

    destinations = Destination.objects.filter(source="dida", adminLevel=1)
    countries = {destination.sourceId: destination for destination in destinations}

    cityMap = _getCityMap(cities)
    oneCountryCityMap = {}
    for countryCode, cities in cityMap.items():
        for city in cities.values():
            cityInfo = city["info"]
            subCities = city["subCities"]
            name_en = cityInfo["CityName"]
            name_cn = cityInfo["CityName_CN"] if "CityName_CN" in cityInfo else None
            sourceId = cityInfo["CityCode"]
            countryCode = cityInfo["CountryCode"]

            data = [("name_cn", name_cn), ("name_en", name_en)]
            oneCountryCityMap[sourceId] = (data, subCities)
        destinations = Destination.objects.filter(sourceId__in=oneCountryCityMap.keys(), source="dida")
        destinationExists = {destination.sourceId: destination for destination in destinations}

        jsonDataMap = {}
        newDestinations = []
        for sourceId, (data, subCities) in oneCountryCityMap.items():
            newVersion = generateVersion(data)
            destination = destinationExists[sourceId] if sourceId in destinationExists else None
            update = _generateCountryUpdate(destination, dict(data), newVersion)
            if sourceId in destinationExists:
                if update:
                    DestinationUpdate.objects.filter(destination=destinationExists[destination.sourceId]).update(json=json.dumps(update))
            else:
                newDestinations.append(Destination(sourceId=sourceId, source="dida", adminLevel=2, parent=countries[countryCode]))
                jsonDataMap[sourceId] = json.dumps(update)

        if newDestinations:
            Destination.objects.bulk_create(newDestinations)
            destinations = Destination.objects.filter(source="dida", sourceId__in=jsonDataMap.keys())
            destinations = {destination.sourceId: destination for destination in destinations}

            newSubCities = []
            newDestinationUpdates = []
            for sourceId, jsonData in jsonDataMap.items():
                destinationUpdate = DestinationUpdate(destination=destinations[sourceId], json=jsonData)
                newDestinationUpdates.append(destinationUpdate)

                for cityId in oneCountryCityMap[sourceId][1]:
                    subCity = DestinationSubCity(destination=destinations[sourceId], cityId=cityId)
                    newSubCities.append(subCity)
            DestinationUpdate.objects.bulk_create(newDestinationUpdates)
            DestinationSubCity.objects.bulk_create(newSubCities)
        oneCountryCityMap = {}


def _getHotelMap(hotels):
    hotelMap = {}
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
        hotelMap.setdefault(countryCode, []).append((cityId, sourceId, data))
    return hotelMap


def normalizeDidaHotel():
    dida = Dida.objects.filter().order_by("-created").first()
    filePath = os.path.join(settings.STATICFILES_DIRS[0], "dida", dida.hotelFile)
    hotelFile = open(filePath, "r", encoding="utf-8")
    hotels = hotelFile.read()

    subCities = DestinationSubCity.objects.filter().prefetch_related("destination")
    destinationMap = {}
    for subCity in subCities:
        destinationMap[subCity.cityId] = subCity.destination

    hotelMap = _getHotelMap(hotels)
    for countryCode, oneCountryHotels in hotelMap.items():
        sourceIds = [hotel[1] for hotel in oneCountryHotels]
        hotels = Hotel.objects.filter(sourceId__in=sourceIds, source="dida")
        hotelExists = {hotel.sourceId: hotel for hotel in hotels}

        newHotels = []
        jsonDataMap = {}
        for cityId, sourceId, data in oneCountryHotels:
            newVersion = generateVersion(data)
            data = dict(data)
            hotel = hotelExists[sourceId] if sourceId in hotelExists else None
            update = _generateHotelUpdate(hotel, data, newVersion)
            if sourceId in hotelExists:
                if update:
                    HotelUpdate.objects.filter(hotel=hotelExists[hotel.sourceId]).update(json=json.dumps(update))
            else:
                newHotels.append(Hotel(sourceId=sourceId, source="dida", longitude=data["longitude"], latitude=data["latitude"], destination=destinationMap[cityId]))
                jsonDataMap[sourceId] = json.dumps(update)

        if newHotels:
            startIndex = 0
            createHotels = newHotels[startIndex:1000]
            while createHotels:
                Hotel.objects.bulk_create(createHotels)
                startIndex += 1000
                createHotels = newHotels[startIndex:startIndex+1000]
            hotels = Hotel.objects.filter(source="dida", sourceId__in=jsonDataMap.keys())
            hotels = {hotel.sourceId: hotel for hotel in hotels}

            newHotelUpdates = []
            for sourceId, jsonData in jsonDataMap.items():
                hotelUpdate = HotelUpdate(hotel=hotels[sourceId], json=jsonData)
                newHotelUpdates.append(hotelUpdate)
            HotelUpdate.objects.bulk_create(newHotelUpdates)


def gecodeLocationWithHotelInfo():
    destinations = Destination.objects.filter(adminLevel=2,
                                              source="dida",
                                              longitude__isnull=True,
                                              latitude__isnull=True).prefetch_related("hotels").order_by("id")

    for destination in destinations:
        hotels = destination.hotels.all()
        if not hotels:
            continue

        longitude, latitude = calculateCenterPos([(hotel.longitude, hotel.latitude) for hotel in hotels])
        destination.longitude = longitude
        destination.latitude = latitude
        destination.save()


def geocodeLocationWithMapApi():
    count = 0
    destinations = Destination.objects.filter(source="dida",
                                              longitude__isnull=True,
                                              latitude__isnull=True).prefetch_related("update").order_by("id")

    client = GoogleMapClient()
    for destination in destinations:
        jsonData = json.loads(destination.update.json)
        longitude, latitude = client.searchLocation(jsonData["name_en"])
        if longitude and latitude:
            destination.longitude = longitude
            destination.latitude = latitude
            destination.save()
        count += 1
        if count >= 1000:
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
