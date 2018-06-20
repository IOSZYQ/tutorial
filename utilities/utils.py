__author__ = 'HanHui'

import re
import copy
import hashlib
import logging
import requests
import collections
from math import cos, sin, atan2, sqrt, pi ,radians, degrees

adtwLogger = logging.getLogger("ADTW")

REQUEST_TIMEOUT = 60

CURRENCY_MAP = {
    "cny": 0,
    "usd": 1,
    "aud": 2,
    "cad": 3,
    "hkd": 4,
    "gbp": 5,
    "eur": 6,
    "jpy": 7,
    "nzd": 8,
    "sgd": 9,
    "thb": 10,
    "krw": 11,
    "twd": 12,
    "chf": 13,
    "sek": 14,
    "dkk": 15,
    "rub": 16,
    "nok": 17,
    "php": 18,
    "mop": 19,
    "idr": 20,
    "brl": 21,
    "aed": 22,
    "inr": 23,
    "zar": 24
}


def generateVersion(data):
    md5 = hashlib.md5()

    dataStr = ""
    for key, value in data:
        if not value:
            value = ""
        dataStr += "{0}={1}|".format(key, value)
    dataStr = dataStr.rstrip("|")

    md5.update(dataStr.encode(encoding='utf-8'))
    return md5.hexdigest()


def getCurrencyCode(currency):
    if currency.lower() in CURRENCY_MAP:
        return CURRENCY_MAP[currency.lower()]
    else:
        return None


def extractData(oriData, fields=None):
    if fields == None:
        return copy.deepcopy(oriData)

    if oriData == None:
        return None

    result = {}

    for k, v in fields.items():
        if k not in oriData:
            continue

        oriValue = oriData[k]
        if isinstance(v, collections.Mapping) and oriValue != None:
            if isinstance(oriValue, list):
                result[k] = [extractData(oriItem, v) for oriItem in oriValue]
            else:
                result[k] = extractData(oriValue, v)
        elif v:
            result[k] = copy.deepcopy(oriValue)

    return result


def safeRequests(url):
    adtwLogger.debug(url)
    for x in range(0, 6):
        try:
            return requests.get(url, timeout=REQUEST_TIMEOUT)
        except Exception as e:
            if x >= 5:
                raise


def clearEmoji(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)


def updatedObjAttr(obj, attr, value, updatedFields):
    if getattr(obj, attr) != value:
        updatedFields.append(attr)
        setattr(obj, attr, value)


def calculateCenterPos(locations):
    x = 0
    y = 0
    z = 0
    if len(locations) == 1:
        return locations[0]["lng"], locations[0]["lat"]

    lenth = len(locations)
    for location in locations:
        lon = radians(float(location["lng"]))
        lat = radians(float(location["lat"]))

        x += cos(lat) * cos(location["lng"])
        y += cos(lat) * sin(location["lng"])
        z += sin(lat)

    x = float(x / lenth)
    y = float(y / lenth)
    z = float(z / lenth)
    return (degrees(atan2(y, x)), degrees(atan2(z, sqrt(x * x + y * y))))


def calculateBounds(locations):
    latitudes = sorted([location["lat"] for location in locations])
    longitudes = sorted([location["lng"] for location in locations])

    latS = latitudes[0]
    latN = latitudes[-1]
    latDist = latN - latS
    latN += latDist / 20
    if latN > 85:
        latN = 85

    latS -= latDist / 20
    if latS < -85:
        latS = -85


    lngW = longitudes[0]
    lngE = longitudes[-1]
    minLngDis = lngE - lngW

    for i in range(0, len(longitudes) - 1):
        lngDis = longitudes[i] - longitudes[i + 1] + 360
        if lngDis < minLngDis:
            minLngDis = lngDis
            lngE = longitudes[i]
            lngW = longitudes[i + 1]

    lngE += minLngDis / 20
    if lngE > 180:
        lngE -= 360

    lngW -= minLngDis / 20
    if lngW < -180:
        lngW += 360

    return {
        "latN": latN,
        "latS": latS,
        "lngE": lngE,
        "lngW": lngW
    }
