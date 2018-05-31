__author__ = "HanHui"

import json
import requests
import projectConfig


class DidaClient(object):
    @classmethod
    def _fetchData(cls, url, params=None):
        requestDict = {
            "Header": {
                "ClientID": projectConfig.DIDA_CLIENT_ID,
                "LicenseKey": projectConfig.DIDA_LICENSE_KEY
            }
        }
        if params:
            requestDict.update(params)

        headers = {
            "Accept-Encoding": "gzip"
        }
        r = requests.post(url=projectConfig.DIDA_URL+url, json=requestDict, headers=headers)
        if r.status_code != 200:
            raise Exception("post fail, url={0}, status={1}".format(url, r.status_code))

        try:
            content = json.loads(r.text)
        except:
            content = None

        if not content or ('Success' not in content and "Url" not in content):
            raise Exception("api fail, url={0} content={1}".format(url, r.text))

        if "Success" in content:
            if "PriceDetails" in content["Success"] and "HotelList" in content["Success"]["PriceDetails"]:
                return content["Success"]["PriceDetails"]["HotelList"]
            return content['Success']
        else:
            r = requests.get(content["Url"])
            return r.text

    def downCountryList(self):
        return self._fetchData('/api/staticdata/GetCountryList?$format=json')

    def downCityList(self, countryCode):
        params = {
          "IncludeSubCity": True,
          "CountryCode": countryCode
        }
        return self._fetchData('/api/staticdata/GetCityList?$format=json', params=params)

    def downGetStaticInformation(self):
        params = {
          "IsGetUrlOnly": True,
          "StaticType": "HotelSummary"
        }
        return self._fetchData('/api/staticdata/GetStaticInformation?$format=json', params=params)

    def searchHotelPrices(self, checkIn, checkOut, cityCode, star, countPerPage, pageNum):
        params = {
            "CheckOutDate": checkOut,
            "CheckInDate": checkIn,
            "Destination": {
                "CityCode": cityCode
            },
            "LowestPriceOnly": True
        }
        filterList = {}
        if star is not None:
            filterList.update({
                "StarRating": star
            })
        if countPerPage is not None and pageNum is not None:
            filterList.update({
                "Pagination": {
                    "CountPerPage": countPerPage,
                    "PageNum": pageNum
                }
            })
        if filterList:
            params.update({"FilterList": filterList})
        return self._fetchData('/api/rate/pricesearch?$format=json', params=params)
