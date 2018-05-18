# _*_ coding: utf-8 _*_
__author__ = 'alan'
__date__ = '2018/4/10 下午2:06'


import hashlib
import time
import urllib.request
import urllib.parse
import json
import gzip
import requests
from io import StringIO
import base64

from projectConfig import *

partnerId=PKFARE_PARTNERID
partnerKey=PKFARE_PARTNERKEY
sign=hashlib.md5("{}{}".format(partnerId,partnerKey).encode("utf-8")).hexdigest()
# #单程
# data={
#     "authentication": {
#         "partnerId": partnerId,
#         "sign": sign
#     },
#     "search": {
#         "adults": 1,
#         "airline": "",
#         "children": 1,
#         "nonstop": 0,
#         "searchAirLegs": [
#             {
#                 "cabinClass": "Economy",
#                 "departureDate": "2018-05-12",
#                 "destination": "BKK",
#                 "origin": "HKG"
#             }
#         ],
#         "solutions": 20
#     }
# }
#往返
data={
    "authentication": {
        "partnerId": partnerId,
        "sign": sign
    },
    "search": {
        "adults": 1,
        "airline": "",
        "children": 1,
        "nonstop": 0,
        "searchAirLegs": [
            {
                "cabinClass": "Economy",
                "departureDate": "2018-05-19",
                "destination": "HKG",
                "origin": "MEL"
            },
            {
                "cabinClass": "Economy",
                "departureDate": "2018-05-15",
                "destination": "MEL",
                "origin": "HKG"
            }
        ],
        "solutions": 20
    }
}
data = base64.b64encode(bytes(str(data),'utf-8'))
param = {"param":data}
url="http://open.pkfare.com/apitest/shopping"

r = requests.get(url=url,params=param)
print(r.url)
gzipFile = gzip.GzipFile(fileobj=r)
r=gzipFile.fileobj.content
de_data = gzip.decompress(r)
print(str(de_data))
