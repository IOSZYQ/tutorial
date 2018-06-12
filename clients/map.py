__author__ = "HanHui"

import json
import certifi
import requests
import projectConfig


class GoogleMapClient(object):
    @classmethod
    def _fetchData(cls, address, region):
        params = {
            "address": address,
            "key": projectConfig.GOOGLE_MAP_KEY,
            "region": region
        }

        r = requests.get(url=projectConfig.GOOGLE_MAP_URL, params=params, verify=certifi.where())
        print(r.text)
        if r.status_code != 200:
            return None, None

        try:
            data = json.loads(r.text)
            location = data["results"][0]["geometry"]["location"]
            return location["lng"], location["lat"]
        except:
            return None, None

    def searchLocation(self, address, region):
        return self._fetchData(address, region)
