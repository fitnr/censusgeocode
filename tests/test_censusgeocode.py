#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of censusgeocode.
# https://github.com/fitnr/censusgeocode

# Licensed under the General Public License (version 3)
# http://opensource.org/licenses/LGPL-3.0
# Copyright (c) 2015, Neil Freeman <contact@fakeisthenewreal.org>

import unittest
from censusgeocode import CensusGeocode
from censusgeocode.censusgeocode import CensusResult


class CensusGeoCodeTestCase(unittest.TestCase):

    cg = None

    def setUp(self):
        self.cg = CensusGeocode(benchmark='Public_AR_ACS2014', geovintage='ACS2013')

    def test_returns(self):
        results = self.cg.coordinates(-74, 43)
        assert isinstance(results, CensusResult)

    def test_coords(self):
        results = self.cg.coordinates(-74, 43)
        assert results.geographies['Counties'][0]['BASENAME'] == 'Saratoga'
        assert results.geographies['Counties'][0]['GEOID'] == '36091'
        assert results.geographies['Census Tracts'][0]['BASENAME'] == "615"
