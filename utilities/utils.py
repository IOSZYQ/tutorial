__author__ = 'HanHui'

import re
import copy
import logging
import requests
import collections

adtwLogger = logging.getLogger("ADTW")

REQUEST_TIMEOUT = 60


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
