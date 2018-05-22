__author__ = 'swolfod'

from utilities import utils, DataSerializer, djangoUtils
from images import imageUtils
from .models import *
import apiUtils

class DestinationSerializer(DataSerializer):

    def __init__(self, destination, fields=None, parameters=None):
        if isinstance(destination, int) or isinstance(destination, str):
            destination = Destination.objects.get(pk=destination)

        super(DestinationSerializer, self).__init__(destination, fields, {
            "type": "adminLevel",
            "introduction": "description"
        })

        if not parameters:
            parameters = {}

        self._destination = destination
        self._fields = fields
        self._coverW = parameters.get("coverW")
        self._coverH = parameters.get("coverH")


    def coverPic(self, fields=None):
        return imageUtils.patternImageUrl(self._destination.pic, 1, width=self._coverW, height=self._coverH, static=True)


    def countryFlag(self, fields=None):
        if self._destination.adminLevel != 1:
            return None

        try:
            return imageUtils.patternImageUrl(self._destination.flag.flagImage, 1, static=True)
        except:
            return None


    def bounds(self, fields=None):
        result = {
            "latitudeN":    self._destination.latitudeN,
            "latitudeS":    self._destination.latitudeS,
            "longitudeE":   self._destination.longitudeE,
            "longitudeW":   self._destination.longitudeW,
        }

        return utils.extractData(result, fields)


    def parent(self, fields=None):
        return DestinationSerializer(self._destination.parent, fields).data


    def shapes(self, fields=None):
        shapePoints = self._destination.shapePoints.order_by("index").all()

        return [{
            "latitude": shapePoint.latitude,
            "longitude": shapePoint.longitude
        } for shapePoint in shapePoints]


    def recommendedCities(self, fields=None):
        if fields == None:
            fields = True

        citiesQuery = Destination.objects.filter(adminLevel=2, inactive=False)
        if self._destination.adminLevel == 0:
            citiesQuery = citiesQuery.filter(parent__parent_id=self._destination.id, weight__gte=200).order_by("-weight")
            cities = citiesQuery[:10]
        else:
            citiesQuery = citiesQuery.filter(parent_id=self._destination.id, weight__gte=100).order_by("-weight")
            cities = citiesQuery[:500]

        majorCities = [city for city in cities if city.weight >= 200]
        cities = [city for city in cities if city.weight < 200]

        if fields is True or fields.get("majorCities") is True:
            majorCities = [djangoUtils.encodeId(city.id) for city in majorCities]
        else:
            majorCities = [DestinationSerializer(city, fields.get("majorCities"), self._attrMap).data for city in majorCities]

        if fields is True or fields.get("cities") is True:
            cities = [djangoUtils.encodeId(city.id) for city in cities]
        else:
            cities = [DestinationSerializer(city, fields.get("cities"), self._attrMap).data for city in cities]

        return {
            "majorCities": majorCities,
            "cities": cities
        }


    def subCountries(self, fields=None):
        if fields == None:
            fields = True

        countries = Destination.objects.filter(adminLevel=1, parent_id=self._destination.id, inactive=False).all()
        majorCountries = [country.id for country in countries if country.weight >= 200]
        popularCountries = [country.id for country in countries if country.weight >= 100]

        if fields is True or fields.get("countries") is True:
            countries = [djangoUtils.encodeId(country.id) for country in countries]
        else:
            countries = [DestinationSerializer(country, fields.get("countries"), self._attrMap).data for country in countries]

        popularCountries = [djangoUtils.encodeId(countryId) for countryId in popularCountries] \
            if fields is True or fields.get("popularCountries") else None

        majorCountries = [djangoUtils.encodeId(countryId) for countryId in majorCountries] \
            if fields is True or fields.get("majorCountries") else None

        return {
            "countries"         : countries,
            "majorCountries"    : majorCountries,
            "popularCountries"  : popularCountries
        }


    def aliases(self, fields=None):
        return [alias.alias for alias in self._destination.aliases.all()]


    def defaultCard(self, fields=None):
        card = self._destination.cards.first()
        return apiUtils.normalizeContent(card.content, fields) if card else None


    def infos(self, fields=None):
        infos = self._destination.infos.all()
        return [{"title": info.infoTitle, "content": info.infoContent} for info in infos]


    def visaInfo(self, fields=None):
        if self._destination.adminLevel != 1:
            return None

        try:
            return apiUtils.normalizeContent(self._destination.visa.content, fields)
        except Exception as e:
            return None

    def creatorId(self, fields=None):
        return djangoUtils.encodeId(self._destination.creatorId) if self._destination.creatorId else None
