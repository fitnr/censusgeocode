"""Tests for censusgeocode"""

# This file is part of censusgeocode.
# https://github.com/fitnr/censusgeocode

# Licensed under the General Public License (version 3)
# http://opensource.org/licenses/LGPL-3.0
# Copyright (c) 2015-2026, Neil Freeman <contact@fakeisthenewreal.org>

import random
import string
import warnings
from pathlib import Path
from typing import Union

import pytest
import vcr

from censusgeocode import CensusGeocode
from censusgeocode.censusgeocode import GeographyResult


@vcr.use_cassette("tests/fixtures/coordinates.yaml")
def test_coords(cg: CensusGeocode) -> None:
    results = cg.coordinates(-74, 43)
    assert isinstance(results, GeographyResult)
    assert results.input
    assert results["Counties"][0]["BASENAME"] == "Saratoga"
    assert results["Counties"][0]["GEOID"] == "36091"
    assert results["Census Tracts"][0]["BASENAME"] == "615"


def test_url(cg: CensusGeocode) -> None:
    r = cg._geturl("coordinates", "geographies")
    assert r == "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"


@vcr.use_cassette("tests/fixtures/address-geographies.yaml")
def test_address_zipcode(cg: CensusGeocode) -> None:
    results = cg.address(
        "1600 Pennsylvania Avenue NW", city="Washington", state="DC", zipcode="20500"
    )
    assert results[0]
    assert (
        results[0]["geographies"]["Counties"][0]["BASENAME"] == "District of Columbia"
    )


@vcr.use_cassette("tests/fixtures/address-geographies.yaml")
def test_address_zip(cg: CensusGeocode) -> None:
    results = cg.address(
        "1600 Pennsylvania Avenue NW", city="Washington", state="DC", zip="20500"
    )
    assert results[0]
    assert (
        results[0]["geographies"]["Counties"][0]["BASENAME"] == "District of Columbia"
    )


@vcr.use_cassette("tests/fixtures/onelineaddress.yaml")
def test_onelineaddress(cg: CensusGeocode) -> None:
    results = cg.onelineaddress(
        "1600 Pennsylvania Avenue NW, Washington, DC, 20500", layers="all"
    )
    assert results[0]

    assert (
        results[0]["geographies"]["Counties"][0]["BASENAME"] == "District of Columbia"
    )
    assert "Metropolitan Divisions" in results[0]["geographies"]
    assert "Alaska Native Village Statistical Areas" in results[0]["geographies"]


@vcr.use_cassette("tests/fixtures/address-locations.yaml")
def test_address_return_type(cg: CensusGeocode) -> None:
    results = cg.address(
        "1600 Pennsylvania Avenue NW",
        city="Washington",
        state="DC",
        zipcode="20500",
        returntype="locations",
    )
    assert (
        results[0]["matchedAddress"].upper()
        == "1600 PENNSYLVANIA AVE NW, WASHINGTON, DC, 20502"
    )
    assert results[0]["addressComponents"]["streetName"] == "PENNSYLVANIA"


@vcr.use_cassette("tests/fixtures/test_benchmark_vintage.yaml")
def test_benchmark_vintage() -> None:
    """Tests custom initialization logic independently of the default fixture."""
    bmark = "Public_AR_Census2020"
    vint = "Census2020_Current"
    cg_custom = CensusGeocode(benchmark=bmark, vintage=vint)
    result = cg_custom.address(
        "1600 Pennsylvania Avenue NW",
        city="Washington",
        state="DC",
        zipcode="20500",
        returntype="geographies",
    )
    assert result.input["benchmark"]["benchmarkName"] == bmark
    assert result.input["vintage"]["vintageName"] == vint
    assert result[0]["geographies"]["Census Tracts"][0]["GEOID"] == "11001006202"


def test_set_vintage(cg: CensusGeocode) -> None:
    """Test changing vintage."""
    vint = "".join(random.choices(string.ascii_letters, k=8))
    cg.set_vintage(vint)
    assert cg.vintage == vint


def test_set_benchmark(cg: CensusGeocode) -> None:
    """Test changing benchmark."""
    bmark = "".join(random.choices(string.ascii_letters, k=8))
    cg.set_benchmark(bmark)
    assert cg.benchmark == bmark


@vcr.use_cassette("tests/fixtures/address-batch.yaml")
@pytest.mark.parametrize(
    "batch_input",
    ["tests/fixtures/batch.csv", Path("tests/fixtures/batch.csv")],
    ids=["string", "pathlib.Path"],
)
def test_addressbatch(cg: CensusGeocode, batch_input: Union[str, Path]) -> None:
    """addressbatch() method works with varied input types."""
    result = cg.addressbatch(batch_input, returntype="locations")
    assert isinstance(result, list)
    resultdict = {int(res["id"]): res for res in result}
    assert resultdict[3]["parsed"] == "3 GRAMERCY PARK W, NEW YORK, NY, 10003"
    assert resultdict[2]["match"] is False

    result_geo = cg.addressbatch(batch_input, returntype="geographies")
    assert isinstance(result_geo, list)
    resultdict_geo = {int(res["id"]): res for res in result_geo}
    assert resultdict_geo[3]["tigerlineid"] == "59653655"
    assert resultdict_geo[3]["statefp"] == "36"


@pytest.mark.parametrize(
    "bad_file",
    [r"tests/fixtures/nonexistent.csv", Path("tests/fixtures/nonexistent.csv")],
    ids=["string", "pathlib.Path"],
)
def test_addressbatch_file_not_found(
    cg: CensusGeocode, bad_file: Union[str, Path]
) -> None:
    """addressbatch() method raises error when file not found."""
    with pytest.raises(FileNotFoundError, match="File not found at path"):
        cg.addressbatch(bad_file, returntype="locations")

    with pytest.raises(FileNotFoundError, match="File not found at path"):
        cg.addressbatch(bad_file, returntype="geographies")


def test_warning10k(cg: CensusGeocode) -> None:
    """Sending more than 10,000 records to batch raises a warning."""
    warnings.simplefilter("error")
    result = []
    with pytest.raises(UserWarning, match="Sending more than 10,000 records"):
        result = cg.addressbatch({} for _ in range(10001))
    assert result == []
