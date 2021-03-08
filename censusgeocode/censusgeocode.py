#!/usr/bin/env python3

# Copyright (C) 2015-9 Neil Freeman

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Census Geocoder wrapper
see http://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.pdf
Accepts either named `lat` and `lng` or x and y inputs.
"""
import csv
import io
from six import string_types
import requests
from requests.exceptions import RequestException
from requests_toolbelt.multipart.encoder import MultipartEncoder


DEFAULT_BENCHMARK = 'Public_AR_Current'
DEFAULT_VINTAGE = 'Current_Current'


class CensusGeocode(object):
    '''Fetch results from the Census Geocoder'''
    _url = "https://geocoding.geo.census.gov/geocoder/{returntype}/{searchtype}"
    returntypes = ['geographies', 'locations']

    batchfields = {
        'locations': ['id', 'address', 'match', 'matchtype', 'parsed', 'coordinate', 'tigerlineid', 'side'],
        'geographies': ['id', 'address', 'match', 'matchtype', 'parsed', 'coordinate',
                        'tigerlineid', 'side', 'statefp', 'countyfp', 'tract', 'block']
    }

    def __init__(self, benchmark=None, vintage=None):
        '''
        Arguments:
            benchmark (str): A name that references the version of the locator to use.
                See https://geocoding.geo.census.gov/geocoder/benchmarks
            vintage (str): The geography part of the desired vintage.
                See: https://geocoding.geo.census.gov/geocoder/vintages?form

        >>> CensusGeocode(benchmark='Public_AR_Current', vintage='Current_Current')
        '''
        self._benchmark = benchmark or DEFAULT_BENCHMARK
        self._vintage = vintage or DEFAULT_VINTAGE

    def _geturl(self, searchtype, returntype=None):
        returntype = returntype or self.returntypes[0]
        return self._url.format(returntype=returntype, searchtype=searchtype)

    def _fetch(self, searchtype, fields, **kwargs):
        '''Fetch a response from the Geocoding API.'''
        fields['vintage'] = self.vintage
        fields['benchmark'] = self.benchmark

        fields['format'] = 'json'

        if 'layers' in kwargs:
            fields['layers'] = kwargs['layers']

        returntype = kwargs.get('returntype', 'geographies')
        url = self._geturl(searchtype, returntype)

        try:
            with requests.get(url, params=fields, timeout=kwargs.get('timeout')) as r:
                content = r.json()
                if "addressMatches" in content.get('result', {}):
                    return AddressResult(content)

                if "geographies" in content.get('result', {}):
                    return GeographyResult(content)

                raise ValueError()

        except (ValueError, KeyError):
            raise ValueError("Unable to parse response from Census")

        except RequestException as e:
            raise e

    def coordinates(self, x, y, **kwargs):
        '''Geocode a (lon, lat) coordinate.'''
        kwargs['returntype'] = 'geographies'
        fields = {
            'x': x,
            'y': y
        }

        return self._fetch('coordinates', fields, **kwargs)

    def address(self, street, city=None, state=None, zipcode=None, **kwargs):
        '''Geocode an address.'''
        fields = {
            'street': street,
            'city': city,
            'state': state,
            'zip': zipcode,
        }

        return self._fetch('address', fields, **kwargs)

    def onelineaddress(self, address, **kwargs):
        '''Geocode an an address passed as one string.
        e.g. "4600 Silver Hill Rd, Suitland, MD 20746"
        '''
        fields = {
            'address': address,
        }

        return self._fetch('onelineaddress', fields, **kwargs)

    def set_benchmark(self, benchmark):
        self._benchmark = benchmark

    @property
    def benchmark(self):
        return getattr(self, '_benchmark')

    def set_vintage(self, vintage):
        self._vintage = vintage

    @property
    def vintage(self):
        return getattr(self, '_vintage')

    def _parse_batch_result(self, data, returntype):
        try:
            fieldnames = self.batchfields[returntype]
        except KeyError:
            raise ValueError('unknown returntype: {}'.format(returntype))

        def parse(row):
            row['lat'], row['lon'] = None, None

            if row['coordinate']:
                try:
                    row['lon'], row['lat'] = tuple(float(a) for a in row['coordinate'].split(','))
                except:
                    pass

            del row['coordinate']
            row['match'] = row['match'] == 'Match'
            return row

        # return as list of dicts
        with io.StringIO(data) as f:
            reader = csv.DictReader(f, fieldnames=fieldnames)
            return [parse(row) for row in reader]

    def _post_batch(self, data=None, f=None, **kwargs):
        returntype = kwargs.get('returntype', 'geographies')
        url = self._geturl('addressbatch', returntype)

        if data is not None:
            # For Python 3, compile data into a StringIO
            f = io.StringIO()
            writer = csv.DictWriter(f, fieldnames=['id', 'street', 'city', 'state', 'zip'])
            for i, row in enumerate(data):
                row.setdefault('id', i)
                writer.writerow(row)

            f.seek(0)

        elif f is None:
            raise ValueError('Need either data or a file for CenusGeocode.addressbatch')

        try:
            form = MultipartEncoder(fields={
                'vintage': self.vintage,
                'benchmark': self.benchmark,
                'addressFile': ('batch.csv', f, 'text/plain')
            })
            h = {'Content-Type': form.content_type}

            with requests.post(url, data=form, timeout=kwargs.get('timeout'), headers=h) as r:
                # return as list of dicts
                return self._parse_batch_result(r.text, returntype)

        except RequestException as e:
            raise e

        finally:
            f.close()

    def addressbatch(self, data, **kwargs):
        '''
        Send either a CSV file or data to the addressbatch API.
        According to the Census, "there is currently an upper limit of 1000 records per batch file."
        If a file, must have no header and fields id,street,city,state,zip
        If data, should be a list of dicts with the above fields (although ID is optional)
        '''
        # Does data quack like a file handle?
        if hasattr(data, 'read'):
            return self._post_batch(f=data, **kwargs)

        # Check if it's a string file
        if isinstance(data, string_types):
            with open(data, 'rb') as f:
                return self._post_batch(f=f, **kwargs)

        # Otherwise, assume a list of dicts
        return self._post_batch(data=data, **kwargs)


class GeographyResult(dict):

    _coordkeys = ('CENTLON', 'CENTLAT', 'INTPTLON', 'INTPTLAT')

    def __init__(self, data):
        self.input = data['result'].get('input', {})
        super(GeographyResult, self).__init__(data['result']['geographies'])

        # create float coordinate tuples
        for geolist in self.values():
            for geo in geolist:
                try:
                    geo['CENT'] = float(geo['CENTLON']), float(geo['CENTLAT'])
                except ValueError:
                    geo['CENT'] = ()

                try:
                    geo['INTPT'] = float(geo['INTPTLON']), float(geo['INTPTLAT'])
                except ValueError:
                    geo['INTPT'] = ()


class AddressResult(list):

    def __init__(self, data):
        self.input = data['result'].get('input', {})
        super(AddressResult, self).__init__(data['result']['addressMatches'])
