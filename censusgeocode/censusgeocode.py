#!/usr/local/bin/python3

"""
Census Geocoder wrapper
see http://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.pdf
Accepts either named `lat` and `lng` or x and y inputs.
"""

from urllib import parse, request
from io import StringIO
from itertools import chain
from urllib.error import URLError, HTTPError
from poster.encode import multipart_encode
import csv
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
        '''Send a batch geocoding request.
        data -- An iterable of iterables containing addresses. Each row should contain:
            * House Number and Street Name,
            * City,
            * State,
            * ZIP Code

        If a value is missing, the list must contain an empty string or None.

        For example:
        >>> data = [
        ...     ['1600 Pennsylvania Avenue', 'Washington', 'DC', '20502'],
        ...     ['350 Fifth Avenue', 'New York', 'NY', None],
        ...     ['233 South Wacker Drive', None, None, '60606']
        ... ]

        Optionally, a unique numeric ID can be given as 0th item in each row.
        >>> data = [
        ...     ['101', '400 Broad Street', 'Seattle', 'WA', '98109'],
        ...     ['102', '298 1st St', 'Darwin', 'MN', '55324'],
        ... ]

        returntype --- 'geographies' or 'locations'. Default: geographies
        '''

        # >>> data = urllib.parse.urlencode({'spam': 1, 'eggs': 2, 'bacon': 0})
        # >>> data = data.encode('utf-8')
        # >>>
        # >>> # adding charset parameter to the Content-Type header.
        # >>> request.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
        # >>> with urllib.request.urlopen(request, data) as f:
        # ...     print(f.read().decode('utf-8'))

        fields = {
            'returntype': returntype
        }

        stringio = StringIO()
        writer = csv.writer(stringio, delimiter=',')

        data = iter(data)
        row = list(next(data))

        if len(row) == 4:
            writer.writerow(list(chain([1], row)))
            for id_, row in enumerate(data, 2):
                writer.writerows(list(chain([id_], row)))

        elif len(row) == 5:
            writer.writerow(row)
            writer.writerows(data)

        else:
            raise ValueError("Rows must contain four or five items.")

        # stringio now contains a CSV
        fields['addressFile'] = stringio

        data, headers = multipart_encode(fields)

        url = self._geturl('addressbatch', returntype)

        req = request.Request(url, fields, headers)

        try:
            with request.urlopen(req) as response:
                return response.read()

        except HTTPError as e:
            raise e

        except URLError as e:
            raise e


class CensusResult(object):
    """docstring for CensusResult"""
    def __init__(self, data):
        for key, value in data['result'].items():
            setattr(self, key, value)
