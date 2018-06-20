__author__ = "HanHui"

import json
import certifi
import requests
import projectConfig


class GoogleMapClient(object):
    @classmethod
    def _fetchData(cls, address):
        params = {
            "address": address,
            "key": projectConfig.GOOGLE_MAP_KEY,
        }

        r = requests.get(url=projectConfig.GOOGLE_MAP_URL, params=params, verify=certifi.where())
        if r.status_code != 200:
            return None, None

        try:
            data = json.loads(r.text)
            return data["results"][0]["geometry"]
        except:
            return None

    def searchLocation(self, address):
        return self._fetchData(address)
