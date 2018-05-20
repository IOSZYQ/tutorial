__author__ = "HanHui"

import json
import gzip
import base64
import hashlib
import requests
import projectConfig


class PKFareClient(object):
    @classmethod
    def _fetchData(cls, params=None):
        requestDict = {
            "authentication": {
                "partnerId": projectConfig.PKFARE_PARTNERID,
                "sign": hashlib.md5("{}{}".format(projectConfig.PKFARE_PARTNERID,
                                                  projectConfig.PKFARE_PARTNERKEY).encode("utf-8")).hexdigest()
            }
        }
        if params is not None:
            requestDict.update({"search": params})

        data = base64.b64encode(bytes(str(requestDict), 'utf-8'))
        r = requests.get(url=projectConfig.PKFARE_URL, params={"param": data})
        if r.status_code != 200:
            return None

        gzipFile = gzip.GzipFile(fileobj=r)
        r = gzipFile.fileobj.content
        de_data = gzip.decompress(r)
        return json.loads(de_data)

    def searchFlights(self, depart, arrive, departDate, returnDate=None, cabinClass=None):
        params = {
            "adults": 1,
            "searchAirLegs": [
                {
                    "cabinClass": "Economy" if not cabinClass else cabinClass,
                    "departureDate": departDate,
                    "destination": arrive,
                    "origin": depart
                }
            ],
            "solutions": 20
        }
        if returnDate:
            params["searchAirLegs"].append({
                "cabinClass": "Economy" if not cabinClass else cabinClass,
                "departureDate": returnDate,
                "destination": depart,
                "origin": arrive
            })

        return self._fetchData(params=params)
