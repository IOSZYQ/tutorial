__author__ = 'HanHui'

import os
import csv
import sys
import json
import django
import datetime
from django.conf import settings

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tutorial_Server.settings")
django.setup()

import projectConfig
from clients import DidaClient
from Tutorial.models import Dida


def _saveStaticData(dateStr, countryJson=None, cityJson=None, hotelCsv=None):
    filePath = None
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

if __name__ == "__main__":
    downloadDidaStaticData()
