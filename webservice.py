# _*_ coding: utf-8 _*_
__author__ = 'alan'
__date__ = '2018/4/8 下午4:26'

import suds
import hashlib
import time
import urllib.request
import urllib.parse
import json
import gzip
import requests

from suds.client import Client

url= 'http://ws.51book.com:8000/ltips/services/getAvailableFlightWithPriceAndCommisionService1.0?wsdl'
client = suds.client.Client(url)

agencyCode="LUSHU"
orgAirportCode="PEK"
dstAirportCode="SHA"
date="2018-04-12"
onlyAvailableSeat=1
onlyNormalCommision=1
onlyOnWorkingCommision=1
onlySelfPNR=0
sign="{0}{1}{2}{3}{4}{5}{6}{7}".format(agencyCode,dstAirportCode,onlyAvailableSeat,onlyNormalCommision,onlyOnWorkingCommision,onlySelfPNR,orgAirportCode,'c~P#F41d')
sign = hashlib.md5(sign.encode("utf-8")).hexdigest()

params = {"agencyCode":agencyCode,
          "sign":sign,
          "orgAirportCode":orgAirportCode,
          "dstAirportCode":dstAirportCode,
          "date":date,
          "onlyAvailableSeat":onlyAvailableSeat,
          "onlyNormalCommision":onlyNormalCommision,
          "onlyOnWorkingCommision":onlyOnWorkingCommision,
          "onlySelfPNR":onlySelfPNR,
          }

result = client.service.getAvailableFlightWithPriceAndCommision(params)
print(result)





# url='http://interws.51book.com/lushu/search/searchFlight'
# cabinClass='ECONOMY'
# directFlight=False
# airline='CA'
# routeType='RT'
# resourceChannel=1
# passengerNumberVo=[{"passengerType":"ADT","passengerNumber":1}]
# segmentList=[{"departureAirport":"PEK","arrivalAirport":"MFM","departureTime":"2018-4-20"},{"departureAirport":"MFM","arrivalAirport":"PEK","departureTime":"2018-4-25"}]
# RQData={"cabinClass":cabinClass,
#         "directFlight":directFlight,
#         "airline":airline,
#         "routeType":routeType,
#         "resourceChannel":resourceChannel,
#         "passengerNumberVo":passengerNumberVo,
#         "segmentList":segmentList}
# timeStamp=int(round(time.time() * 1000))
# data={"agencyCode":"lushu",
#       "timeStamp":timeStamp,
#       "RQData":RQData}
# sign=str(json.dumps(data))+'c~P#F41d'
# sign = hashlib.md5(sign.encode("utf-8")).hexdigest()
# print(sign)
# headers={"Content-Type":"application/json",
#          "USERNAME":"LUSHU",
#          "SIGN":sign}
# r = requests.post(url,data=json.dumps(data),headers=headers)
# gzipFile = gzip.GzipFile(fileobj=r)
# r=gzipFile.fileobj.content
# r=r.decode('utf-8')
# print(type(r))
# print(r)
# r=r.replace('true',"True").replace("null","None").replace("false","False")
# print(eval(r))
