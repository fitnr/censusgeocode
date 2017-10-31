#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of censusgeocode.
# https://github.com/fitnr/censusgeocode

# Licensed under the General Public License (version 3)
# http://opensource.org/licenses/LGPL-3.0
# Copyright (c) 2015, Neil Freeman <contact@fakeisthenewreal.org>

import unittest
import vcr
from censusgeocode import CensusGeocode
from censusgeocode.censusgeocode import CensusResult


class CensusGeoCodeTestCase(unittest.TestCase):

    cg = None

    def setUp(self):
        self.cg = CensusGeocode()

    @vcr.use_cassette('tests/fixtures/coordinates.yaml')
    def test_returns(self):
        results = self.cg.coordinates(-74, 43)
        assert isinstance(results, CensusResult)

    @vcr.use_cassette('tests/fixtures/coordinates.yaml')
    def test_input(self):
        results = self.cg.coordinates(-74, 43)
        assert results.input

    @vcr.use_cassette('tests/fixtures/coordinates.yaml')
    def test_coords(self):
        results = self.cg.coordinates(-74, 43)
        assert results[0]['Counties'][0]['BASENAME'] == 'Saratoga'
        assert results[0]['Counties'][0]['GEOID'] == '36091'
        assert results[0]['Census Tracts'][0]['BASENAME'] == "615"

    def test_url(self):
        r = self.cg._geturl('coordinates', 'geographies')
        assert r == 'https://geocoding.geo.census.gov/geocoder/geographies/coordinates'

    @vcr.use_cassette('tests/fixtures/address-geographies.yaml')
    def test_address(self):
        results = self.cg.address('1600 Pennsylvania Avenue NW', city='Washington', state='DC', zipcode='20500')
        assert results[0]
        assert results[0]['geographies']['Counties'][0]['BASENAME'] == 'District of Columbia'

    @vcr.use_cassette('tests/fixtures/onelineaddress.yaml')
    def test_onelineaddress(self):
        results = self.cg.onelineaddress('1600 Pennsylvania Avenue NW, Washington, DC, 20500', layers='all')
        assert results[0]
        try:
            assert results[0]['geographies']['Counties'][0]['BASENAME'] == 'District of Columbia'
        except AssertionError:
            print(results[0]['geographies']['Counties'][0])
            raise

        assert 'Metropolitan Divisions' in results[0]['geographies'].keys()
        assert 'Alaska Native Village Statistical Areas' in results[0]['geographies'].keys()

    @vcr.use_cassette('tests/fixtures/address-locations.yaml')
    def test_address_return_type(self):
        results = self.cg.address('1600 Pennsylvania Avenue NW', city='Washington', state='DC', zipcode='20500', returntype='locations')

        assert results[0]['matchedAddress'].upper() == '1600 PENNSYLVANIA AVE NW, WASHINGTON, DC, 20502'
        assert results[0]['addressComponents']['streetName'] == 'PENNSYLVANIA'

    def test_addressbatch(self):
        with self.assertRaises(NotImplementedError):
            self.cg.addressbatch(None)
