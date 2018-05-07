# _*_ coding: utf-8 _*_
__author__ = 'alan'
__date__ = '2018/4/18 上午11:26'

import requests
import json

from configurationFile import *

baseUrl = 'http://api.didatravel.com'

# # #获取国家列表
# url='/api/staticdata/GetCountryList?$format=json'
data= {}

# #城市数据
# url = '/api/staticdata/GetCityList?$format=json'
# data = {
#   "IncludeSubCity": False,
#   "CountryCode": "CN"
# }

# #床型数据
# url = '/api/staticdata/GetBedTypeList?$format=json'
# data = {}
#
# #早餐数据
# url = '/api/staticdata/GetBreakfastTypeList?$format=json'
# data = {}
#
# #酒店类型
# url = '/api/staticdata/GetPropertyCategoryList?$format=json'
# data = {}
#
# #酒店信息
# url = '/api/staticdata/GetStaticInformation?$format=json'
# data = {
#   "IsGetUrlOnly": True,
#   "StaticType": "HotelSummary"
# }

# # 获取酒店
# url = '/api/rate/pricesearch?$format=json'
# data = {
#     "Destination": {
#         "CityCode": "771"
#     },
#     "LowestPriceOnly": True,
#     "CheckOutDate": "2018-04-27",
#     "CheckInDate": "2018-04-26",
#     "nationality": "CN",
#     "Currency": "CNY"
# }
# data = {
#  "HotelIDList": [1250],
#  "CheckOutDate": "2018-04-30",
#  "CheckInDate": "2018-04-26",
#  "IsRealTime": {
#      "Value": True,
#      "RoomCount": 1
#  },
#  "RealTimeOccupancy": {
#      "ChildCount": 0,
#      "AdultCount": 2,
#      "ChildAgeDetails": []
#  },
#  "nationality": "CN",
#  "Currency": "CNY"
# }

# url = baseUrl + url
data['Header'] = {
    "ClientID": DIDA_CLIENT_ID,
    "LicenseKey": DIDA_LICENSE_KEY
}
# headers = {
# "Acbept-Encoding":"gzip"
# }
#
# r = requests.post(url=url, json=data,headers=headers)
#
# print(data)
# print(url)
# print(r)
# print(r.text)




