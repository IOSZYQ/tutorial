# _*_ coding: utf-8 _*_
__author__ = 'alan'
__date__ = '2018/4/10 下午2:06'

import os
import sys
import django
import hashlib
import time
import urllib.request
import urllib.parse
import json
import gzip
import requests
from io import StringIO
import base64

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tutorial_Server.settings")
django.setup()

# import projectConfig
#
# partnerId=projectConfig.PKFARE_PARTNERID
# partnerKey=projectConfig.PKFARE_PARTNERKEY
# sign=hashlib.md5("{}{}".format(partnerId,partnerKey).encode("utf-8")).hexdigest()
# # #单程
# # data={
# #     "authentication": {
# #         "partnerId": partnerId,
# #         "sign": sign
# #     },
# #     "search": {
# #         "adults": 1,
# #         "airline": "",
# #         "children": 1,
# #         "nonstop": 0,
# #         "searchAirLegs": [
# #             {
# #                 "cabinClass": "Economy",
# #                 "departureDate": "2018-05-12",
# #                 "destination": "BKK",
# #                 "origin": "HKG"
# #             }
# #         ],
# #         "solutions": 20
# #     }
# # }
# #往返
# data={
#     "authentication": {
#         "partnerId": "RksVSX7PfZm1yF04adBWYsCD7M4=",
#         "sign": "17e707b5d9dae8459065dbb139e5f1bd"
#     },
#     "search": {
#         "adults": 1,
#         "airline": "",
#         "children": 1,
#         "nonstop": 0,
#         "searchAirLegs": [
#             {
#                 "cabinClass": "Economy",
#                 "departureDate": "2018-06-16",
#                 "destination": "HKG",
#                 "origin": "BJS"
#             }
#         ],
#         "solutions": 0
#     }
# }
# data = base64.b64encode(bytes(str(data),'utf-8'))
# param = {"param":data}
# url="http://open.pkfare.com/apitest/shopping"
#
# r = requests.get(url=url,params=param)
# gzipFile = gzip.GzipFile(fileobj=r)
# r=gzipFile.fileobj.content
# de_data = gzip.decompress(r)
# print(str(de_data))

from clients.pkfare import PKFareClient
pk = PKFareClient()
print(pk.searchFlights("BJS", "HKG", "2018-07-01", "2018-07-05"))
