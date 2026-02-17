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
For details on the API, see:
https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.pdf
"""

import csv
import io
import warnings
from io import BufferedReader
from pathlib import Path
from typing import Literal, TextIO

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

SearchType = Literal["onelineaddress", "address", "addressPR", "addressbatch", "coordinates"]
ReturnType = Literal["geographies", "locations"]
ResultType = dict[str, str | int | float]


class CensusGeocode:
    """Fetch results from the Census Geocoder"""

    _url = "https://geocoding.geo.census.gov/geocoder/{returntype}/{searchtype}"

    batchfields = {
        "locations": [
            "id",
            "address",
            "match",
            "matchtype",
            "parsed",
            "coordinate",
            "tigerlineid",
            "side",
        ],
        "geographies": [
            "id",
            "address",
            "match",
            "matchtype",
            "parsed",
            "coordinate",
            "tigerlineid",
            "side",
            "statefp",
            "countyfp",
            "tract",
            "block",
        ],
    }

    def __init__(self, benchmark: str = "Public_AR_Current", vintage: str = "Current_Current"):
        """
        Arguments:
            benchmark (str): A name that references the version of the locator to use.
                See https://geocoding.geo.census.gov/geocoder/benchmarks
            vintage (str): The geography part of the desired vintage.
                See: https://geocoding.geo.census.gov/geocoder/vintages?form

        >>> CensusGeocode(benchmark="Public_AR_Current", vintage="Current_Current")
        """
        self._benchmark = benchmark
        self._vintage = vintage

    def _geturl(self, searchtype: SearchType, returntype: ReturnType = "geographies") -> str:
        """Construct an URL for the geocoder."""
        return self._url.format(returntype=returntype, searchtype=searchtype)

    def _fetch(
        self,
        searchtype: SearchType,
        fields: dict[
            Literal["vintage", "benchmark", "layers", "format", "x", "y", "address", "street", "city", "state", "zip"],
            str | float,
        ],
        *,
        returntype: ReturnType = "geographies",
        **kwargs,
    ) -> list | dict:
        """Fetch a response from the Geocoding API."""
        fields["vintage"] = self.vintage
        fields["benchmark"] = self.benchmark

        fields["format"] = "json"

        if "layers" in kwargs:
            fields["layers"] = kwargs["layers"]

        url = self._geturl(searchtype=searchtype, returntype=returntype)

        try:
            with requests.get(url, params=fields, timeout=kwargs.get("timeout")) as r:
                content = r.json()
                if "addressMatches" in content.get("result", {}):
                    return AddressResult(content)

                if "geographies" in content.get("result", {}):
                    return GeographyResult(content)

                raise ValueError

        except (ValueError, KeyError) as e:
            err_msg = "Unable to parse response from Census"
            raise ValueError(err_msg) from e

    def coordinates(self, x: float, y: float, *, returntype: ReturnType = "geographies", **kwargs) -> list | dict:
        """Geocode a (lon, lat) coordinate."""
        fields: dict[Literal["x", "y"], float] = {"x": x, "y": y}

        return self._fetch("coordinates", fields=fields, returntype=returntype, **kwargs)

    def address(
        self,
        street: str,
        city: str | None = None,
        state: str | None = None,
        *,
        zip: str | None = None,
        zipcode: str | None = None,
        **kwargs,
    ) -> list | dict:
        """Geocode an address."""
        fields: dict[Literal["street", "city", "state", "zip"], str] = {
            "street": street,
            "city": city,
            "state": state,
            "zip": zip or zipcode,
        }

        return self._fetch(searchtype="address", fields=fields, **kwargs)

    def onelineaddress(self, address: str, **kwargs) -> list | dict:
        """Geocode an an address passed as one string.
        e.g. "4600 Silver Hill Rd, Suitland, MD 20746"
        """
        fields: dict[Literal["address"], str] = {
            "address": address,
        }

        return self._fetch(searchtype="onelineaddress", fields=fields, **kwargs)

    def set_benchmark(self, benchmark: str) -> None:
        """Set the Census Geocoding API benchmark the class will use.
        See: https://geocoding.geo.census.gov/geocoder/vintages?form"""
        self._benchmark = benchmark

    @property
    def benchmark(self) -> str:
        """Give the Census Geocoding API benchmark the class is using.
        See: https://geocoding.geo.census.gov/geocoder/benchmarks"""
        return self._benchmark

    def set_vintage(self, vintage: str) -> None:
        """Set the Census Geocoding API vintage the class will use.
        See: https://geocoding.geo.census.gov/geocoder/vintages?form"""
        self._vintage = vintage

    @property
    def vintage(self) -> str:
        """Give the Census Geocoding API vintage the class is using.
        See: https://geocoding.geo.census.gov/geocoder/vintages?form"""
        return self._vintage

    def _parse_batch_result(self, data: str, returntype: ReturnType) -> list[ResultType]:
        """Parse the batch address results returned from the Census Geocoding API"""
        try:
            fieldnames = self.batchfields[returntype]
        except KeyError as e:
            err_msg = f"unknown returntype: {returntype}"
            raise ValueError(err_msg) from e

        def parse(row):
            row["lat"], row["lon"] = None, None

            if row["coordinate"]:
                try:
                    row["lon"], row["lat"] = tuple(float(a) for a in row["coordinate"].split(","))
                except ValueError:
                    pass

            del row["coordinate"]
            row["match"] = row["match"] == "Match"
            return row

        # return as list of dicts
        with io.StringIO(data) as f:
            reader = csv.DictReader(f, fieldnames=fieldnames)
            return [parse(row) for row in reader]

    def _post_batch(
        self,
        data: list[dict] | None = None,
        f: TextIO | BufferedReader | None = None,
        *,
        returntype: ReturnType = "geographies",
        **kwargs,
    ) -> list[ResultType]:
        """Send batch address file to the Census Geocoding API"""
        url = self._geturl(searchtype="addressbatch", returntype=returntype)

        if data is None and f is None:
            err_msg = "Need either data or a file for CensusGeocode.addressbatch"
            raise ValueError(err_msg)

        if data:
            f = io.StringIO()
            writer = csv.DictWriter(f, fieldnames=["id", "street", "city", "state", "zip"])
            for i, row in enumerate(data, 1):
                row.setdefault("id", i)
                writer.writerow(row)
                if i == 10001:
                    warnings.warn(
                        "Sending more than 10,000 records, the upper limit for the Census Geocoder. Request will likely fail"
                    )

            f.seek(0)

        try:
            form = MultipartEncoder(
                fields={
                    "vintage": self.vintage,
                    "benchmark": self.benchmark,
                    "addressFile": ("batch.csv", f, "text/plain"),
                }
            )
            headers = {"Content-Type": form.content_type}

            with requests.post(url, data=form, timeout=kwargs.get("timeout"), headers=headers) as r:
                # return as list of dicts
                return self._parse_batch_result(r.text, returntype)

        finally:
            f.close()

    def addressbatch(self, data: TextIO | str | Path | list[dict], **kwargs) -> list[ResultType]:
        """
        Send either a CSV file or data to the addressbatch API.

        According to the Census, "there is currently an upper limit of 10,000 records per batch file."

        If a file, can either be a file-like with a `read()` method, or a `str` that's a path to the
        file. Either way, it must have no header and have fields id,street,city,state,zip

        If data, should be an iterable of dicts with the above fields (although ID is optional).
        """
        # Does data quack like a file handle?
        if hasattr(data, "read"):
            return self._post_batch(f=data, **kwargs)

        # If it is a Path object open the file as bytes
        if isinstance(data, Path):
            with data.open("rb") as f:
                return self._post_batch(f=f, **kwargs)

        # If it is a string, assume it's a filename
        if isinstance(data, str):
            with open(data, "rb") as f:
                return self._post_batch(f=f, **kwargs)

        # Otherwise, assume an iterable of dicts
        return self._post_batch(data=data, **kwargs)


class GeographyResult(dict):
    """Wrapper for geography objects returned by the Census Geocoding API"""

    def __init__(self, data: dict[str, ResultType]) -> None:
        self.input = data["result"].get("input", {})
        super().__init__(data["result"]["geographies"])

        # create float coordinate tuples
        for geolist in self.values():
            for geo in geolist:
                try:
                    geo["CENT"] = float(geo["CENTLON"]), float(geo["CENTLAT"])
                except ValueError:
                    geo["CENT"] = ()

                try:
                    geo["INTPT"] = float(geo["INTPTLON"]), float(geo["INTPTLAT"])
                except ValueError:
                    geo["INTPT"] = ()


class AddressResult(list):
    """Wrapper for address objects returned by the Census Geocoding API"""

    def __init__(self, data: dict[str, ResultType]) -> None:
        self.input = data["result"].get("input", {})
        super().__init__(data["result"]["addressMatches"])
