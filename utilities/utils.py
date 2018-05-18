__author__ = 'HanHui'

import re
import logging
import requests

adtwLogger = logging.getLogger("ADTW")

REQUEST_TIMEOUT = 60


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
