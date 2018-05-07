from django.shortcuts import render

# Create your views here.

import requests
import json

from django.conf import settings
from collections import OrderedDict
from configurationFile import *


# if settings.DEBUG:
BASE_ADDR = "http://api.didatravel.com"
# else:
#     BASE_ADDR = "http://api.didatravel.com/Services/WebService"

class SyncDida(object):
    @classmethod
    def _fetchData(cls,params,url):
        requestDict = OrderedDict([
            ("Header", OrderedDict([
                ("ClientID", DIDA_CLIENT_ID),
                ("LicenseKey", DIDA_LICENSE_KEY)
            ]))
        ])
        requestDict.update(params)
        headers = {
            "Acbept-Encoding": "gzip"
        }
        r = requests.post(url=BASE_ADDR+url, json=requestDict,headers=headers)
        if r.status_code != 200:
            raise Exception("post fail, status={}".format(r.status_code))

        try:
            content = json.loads(r.text)
        except:
            content = None

        if not content or 'Success' not in content:
            raise Exception("api fail, content={}".format(r.text))
        return content['Success']

    def downCountryList(self):
        return self._fetchData(OrderedDict(),'/api/staticdata/GetCountryList?$format=json')

    def downCityList(self,countryCode=''):
        dic = OrderedDict()
        if not countryCode == '':
            data = {
              "IncludeSubCity": False,
              "CountryCode": countryCode
            }
            dic.update(data)
        return self._fetchData(dic, '/api/staticdata/GetCityList?$format=json')

    def downBedTypeList(self):
        return self._fetchData(OrderedDict(), '/api/staticdata/GetBedTypeList?$format=json')

    def downBreakfastTypeList(self):
        return self._fetchData(OrderedDict(), '/api/staticdata/GetBreakfastTypeList?$format=json')

    def downPropertyCategoryList(self):
        return self._fetchData(OrderedDict(), '/api/staticdata/GetPropertyCategoryList?$format=json')

    def downGetStaticInformation(self):
        return self._fetchData(OrderedDict(), '/api/staticdata/GetStaticInformation?$format=json')