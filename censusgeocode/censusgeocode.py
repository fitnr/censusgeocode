#!/usr/local/bin/python3

"""
Census Geocoder wrapper
see http://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.pdf
Accepts either named `lat` and `lng` or x and y inputs.
"""

from urllib import parse, request
from urllib.error import URLError, HTTPError
import json

GEOGRAPHYVINTAGES = ['Current', 'ACS2014', 'ACS2012', 'Census2010']
BENCHMARKS = ['Public_AR_Current', 'Public_AR_ACS2014', 'Public_AR_Census2010']


class CensusGeocode(object):

    _url = "http://geocoding.geo.census.gov/geocoder/{returntype}/{searchtype}"
    returntypes = ['geographies', 'locations']

    def __init__(self, benchmark=None, geographyvintage=None):
        self.benchmark = benchmark or BENCHMARKS[0]
        geographyvintage = geographyvintage or GEOGRAPHYVINTAGES[0]

        self.vintage = geographyvintage + \
            self.benchmark.replace('Public_AR', '')

    def _geturl(self, searchtype, returntype=None):
        returntype = returntype or self.returntypes[0]
        return self._url.format(returntype=returntype, searchtype=searchtype)

    def _fetch(self, searchtype, fields, returntype=None):
        fields['vintage'] = self.vintage
        fields['benchmark'] = self.benchmark

        url = self._geturl(searchtype, returntype) + '?' + parse.urlencode(fields).encode('utf-8')

        try:
            with request.urlopen(url) as response:
                return json.loads(response.read())

        except HTTPError as e:
            raise e

        except URLError as e:
            raise e

    def coordinates(self, x, y, returntype=None):
        fields = {
            'x': x,
            'y': y
        }
        return self._fetch('coordinates', fields, returntype)

    def address(self, street, city=None, state=None, zipcode=None, returntype=None):
        fields = {
            'street': street,
            'city': city,
            'state': state,
            'zip': zipcode,
        }
        return self._fetch('coordinates', fields, returntype)

    def onelineaddress(self, address, returntype=None):
        fields = {
            'address': address,
        }
        return self._fetch('coordinates', fields, returntype)

    def addressbatch(self, data, returntype):
        raise NotImplementedError





class CensusResult(object):
    """docstring for CensusResult"""
    def __init__(self, data):
        for key, value in data['result'].items():
            setattr(self, key, value)
