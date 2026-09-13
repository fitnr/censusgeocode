"""
Census Geocoder wrapper.

For details on the API, see:
https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.pdf
"""

# This file is part of censusgeocode.
# https://github.com/fitnr/censusgeocode

# Licensed under the General Public License (version 3)
# http://opensource.org/licenses/LGPL-3.0
# Copyright (c) 2015-2026, Neil Freeman <contact@fakeisthenewreal.org>

from __future__ import annotations

import contextlib
import csv
import io
import warnings
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Dict, List, Literal, TextIO, Union

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

SearchType = Literal[
    "onelineaddress", "address", "addressPR", "addressbatch", "coordinates"
]
ReturnType = Literal["geographies", "locations"]
ResultType = Dict[str, Union[str, int, float, list]]

DEFAULT_BENCHMARK = "Public_AR_Current"
DEFAULT_VINTAGE = "Current_Current"
DEFAULT_TIMEOUT = 12


class CensusGeocode:
    """Census Geocoder API wrapper."""

    _url = "https://geocoding.geo.census.gov/geocoder/{returntype}/{searchtype}"

    def __init__(
        self, benchmark: str = DEFAULT_BENCHMARK, vintage: str = DEFAULT_VINTAGE
    ) -> None:
        """
        Initialize a CensusGeocode instance.

        Args:
            benchmark (str):
                Name that references the version of the locator to use.
                See https://geocoding.geo.census.gov/geocoder/benchmarks
            vintage (str):
                Geography part of the desired vintage.
                See https://geocoding.geo.census.gov/geocoder/vintages?form

        Example:
            CensusGeocode(benchmark="Public_AR_Current", vintage="Current_Current")

        """
        self._benchmark = benchmark
        self._vintage = vintage
        self.batchfields = {
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

    def _geturl(
        self, searchtype: SearchType, returntype: ReturnType = "geographies"
    ) -> str:
        """
        Construct an URL for the geocoder.

        Args:
            searchtype (SearchType): The type of search to perform.
            returntype (ReturnType): The type of response to return.

        Returns:
            str:
                The constructed URL for the geocoder API request.

        """
        return self._url.format(returntype=returntype, searchtype=searchtype)

    def _fetch(
        self,
        searchtype: SearchType,
        fields: Dict[
            Literal[
                "vintage",
                "benchmark",
                "layers",
                "format",
                "x",
                "y",
                "address",
                "street",
                "city",
                "state",
                "zip",
            ],
            str | float | None,
        ],
        *,
        returntype: ReturnType = "geographies",
        timeout: int = DEFAULT_TIMEOUT,
        layers: str | None = None,
        **kwargs,
    ) -> AddressResult | GeographyResult:
        """
        Fetch a response from the Geocoding API.

        Args:
            searchtype (SearchType): Type of search to perform.
            fields (dict): Parameters of the request.
            returntype (ReturnType): Type of response to return.
            timeout (int): Number of seconds to wait for a response.
            layers (str | None): Layers to include in the response.
            **kwargs: Additional keyword arguments to pass to `requests.get`.

        Returns:
            AddressResult | GeographyResult:
                The response from the Geocoding API.

        """
        fields["vintage"] = self.vintage
        fields["benchmark"] = self.benchmark
        fields["format"] = "json"
        if layers:
            fields["layers"] = layers

        url = self._geturl(searchtype=searchtype, returntype=returntype)

        try:
            with requests.get(url, params=fields, timeout=timeout, **kwargs) as r:
                content = r.json()
                if "addressMatches" in content.get("result", {}):
                    return AddressResult(content)

                if "geographies" in content.get("result", {}):
                    return GeographyResult(content)

                raise ValueError

        except (ValueError, KeyError) as e:
            err_msg = "Unable to parse response from Census"
            raise ValueError(err_msg) from e

    def coordinates(
        self,
        x: float,
        y: float,
        *,
        returntype: ReturnType = "geographies",
        **kwargs,
    ) -> AddressResult | GeographyResult:
        """
        Geocode a (lon, lat) coordinate.

        Args:
            x (float): The longitude coordinate.
            y (float): The latitude coordinate.
            returntype (ReturnType): The type of response to return.
            **kwargs: Additional keyword arguments to pass to `requests.get`.

        Returns:
            AddressResult | GeographyResult:
                The response from the Geocoding API.

        """
        fields: Dict[
            Literal[
                "vintage",
                "benchmark",
                "layers",
                "format",
                "x",
                "y",
                "address",
                "street",
                "city",
                "state",
                "zip",
            ],
            str | float | None,
        ] = {"x": x, "y": y}

        return self._fetch(
            "coordinates", fields=fields, returntype=returntype, **kwargs
        )

    def address(
        self,
        street: str,
        city: str | None = None,
        state: str | None = None,
        *,
        zip: str | None = None,
        zipcode: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
        **kwargs,
    ) -> AddressResult | GeographyResult:
        """
        Geocode an address.

        Args:
            street: The street address.
            city: The city.
            state: The state.
            zip: The ZIP code.
            zipcode: The ZIP code (alternative).
            timeout: The timeout for the request.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            AddressResult | GeographyResult:
                The response from the Geocoding API.

        """
        fields: Dict[
            Literal[
                "vintage",
                "benchmark",
                "layers",
                "format",
                "x",
                "y",
                "address",
                "street",
                "city",
                "state",
                "zip",
            ],
            str | float | None,
        ] = {
            "street": street,
            "city": city,
            "state": state,
            "zip": zip or zipcode,
        }

        return self._fetch(
            searchtype="address", fields=fields, timeout=timeout, **kwargs
        )

    def onelineaddress(self, address: str, **kwargs) -> AddressResult | GeographyResult:
        """
        Geocode an an address passed as one string.

        Args:
            address (str):
                The address to geocode.
                e.g. "4600 Silver Hill Rd, Suitland, MD 20746"
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            AddressResult | GeographyResult:
                The response from the Geocoding API.

        """
        fields: Dict[
            Literal[
                "vintage",
                "benchmark",
                "layers",
                "format",
                "x",
                "y",
                "address",
                "street",
                "city",
                "state",
                "zip",
            ],
            str | float | None,
        ] = {
            "address": address,
        }

        return self._fetch(searchtype="onelineaddress", fields=fields, **kwargs)

    def set_benchmark(self, benchmark: str) -> None:
        """
        Set the Census Geocoding API benchmark the class will use.

        See https://geocoding.geo.census.gov/geocoder/vintages?form

        Args:
            benchmark (str): The benchmark to use in future queries.

        """
        self._benchmark = benchmark

    @property
    def benchmark(self) -> str:
        """
        Give the Census Geocoding API benchmark the class is using.

        See https://geocoding.geo.census.gov/geocoder/benchmarks

        """
        return self._benchmark

    def set_vintage(self, vintage: str) -> None:
        """
        Set the Census Geocoding API vintage the class will use.

        See https://geocoding.geo.census.gov/geocoder/vintages?form

        Args:
            vintage (str): The vintage to use in future queries.

        """
        self._vintage = vintage

    @property
    def vintage(self) -> str:
        """
        Give the Census Geocoding API vintage the class is using.

        See https://geocoding.geo.census.gov/geocoder/vintages?form

        """
        return self._vintage

    def _parse_batch_result(
        self, data: str, returntype: ReturnType
    ) -> List[ResultType]:
        """
        Parse the batch address results returned from the Census Geocoding API.

        Args:
            data (str): The raw response data from the API.
            returntype (ReturnType): The type of result to parse.

        Returns:
            List[ResultType]: The parsed results as a list of dictionaries.

        Raises:
            ValueError: If the returntype is not recognized.

        """
        try:
            fieldnames = self.batchfields[returntype]

        except KeyError as e:
            err_msg = f"unknown returntype: {returntype}"
            raise ValueError(err_msg) from e

        def with_split_coordinates(row: Dict[str, Any]) -> Dict[str, Any]:
            """Return the provided row with `coordinate` field split into `lat`/`lon` and original removed."""
            row["lat"], row["lon"] = None, None

            if row["coordinate"]:
                with contextlib.suppress(ValueError):
                    row["lon"], row["lat"] = tuple(
                        float(a) for a in row["coordinate"].split(",")
                    )

            del row["coordinate"]
            row["match"] = row["match"] == "Match"
            return row

        # return as list of dicts
        with io.StringIO(data) as f:
            reader = csv.DictReader(f, fieldnames=fieldnames)
            return [with_split_coordinates(row) for row in reader]

    def _post_batch(
        self,
        data: Iterable[Dict[str, Any]] | None = None,
        f: io.IOBase | TextIO | None = None,
        *,
        leave_open: bool = False,
        returntype: ReturnType = "geographies",
        timeout: int | None = None,
        **kwargs,
    ) -> List[ResultType]:
        """
        Send batch address file to the Census Geocoding API.

        Args:
            data (Iterable[Dict[str, Any]] | None): The data to send, as an iterable of dictionaries.
            f (io.IOBase | TextIO | None): The file to send, if `data` is not provided.
            leave_open (bool): Whether to leave the file open after sending. Ignored if `data` is provided.
            returntype (ReturnType): The type of result to return.
            timeout (int | None): The timeout for the request, in seconds.
            **kwargs: Additional keyword arguments to pass to `requests.post`.

        Returns:
            List[ResultType]: The parsed results as a list of dictionaries.

        Raises:
            ValueError: If neither data nor a file is provided.

        """
        url = self._geturl(searchtype="addressbatch", returntype=returntype)

        if data is None and f is None:
            err_msg = "Need either data or a file for CensusGeocode.addressbatch"
            raise ValueError(err_msg)

        if not timeout:
            timeout = DEFAULT_TIMEOUT

        if data:
            f = io.StringIO()
            writer = csv.DictWriter(
                f, fieldnames=["id", "street", "city", "state", "zip"]
            )
            for i, row in enumerate(data, 1):
                row.setdefault("id", i)
                writer.writerow(row)
                if i == 10001:
                    warnings.warn(
                        "Sending more than 10,000 records, the upper limit for the Census Geocoder. Request will likely fail.",
                        stacklevel=2,
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

            with requests.post(
                url, data=form, timeout=timeout, headers=headers, **kwargs
            ) as r:
                # return as list of dicts
                return self._parse_batch_result(r.text, returntype)

        finally:
            if f and not leave_open:
                f.close()

    def addressbatch(
        self,
        data: TextIO | str | Path | Iterable[Dict[str, Any]],
        *,
        timeout: int | None = None,
        **kwargs,
    ) -> List[ResultType]:
        """
        Send either a CSV file or data to the addressbatch API.

        According to the Census,
        "there is currently an upper limit of 10,000 records per batch file."

        Args:
            data (TextIO | str | Path | Iterable[Dict[str, Any]]):
                The data to send, either as a file-like object,
                a `Path` object or `str` path, or an iterable of dictionaries.

                - If a file, can either be a file-like with a `read()` method,
                  or a `Path` object or `str` that's a path to the file.
                  Either way, it must have no header and have fields
                  ``id``, ``street``, ``city``, ``state``, and ``zip``.
                - If data, should be an iterable of dicts
                  with the above fields (although ID is optional).

            timeout (int | None): The timeout for the request, in seconds.
            **kwargs: Additional keyword arguments to pass to `requests.post`.

        Returns:
            List[ResultType]: The parsed results as a list of dictionaries.

        Raises:
            TypeError: If the data is not a file-like object, `Path`, `str`, or iterable of dictionaries.

        """
        if isinstance(data, (io.IOBase, TextIO)):
            return self._post_batch(f=data, leave_open=True, timeout=timeout, **kwargs)

        if isinstance(data, str):
            data = Path(data)

        if isinstance(data, Path):
            if not Path(data).exists():
                err_msg = f"File not found at path {data}"
                raise FileNotFoundError(err_msg)
            with data.open("rb") as data_file:
                return self._post_batch(
                    f=data_file, leave_open=True, timeout=timeout, **kwargs
                )

        if isinstance(data, Iterable):
            return self._post_batch(
                data=data, leave_open=False, timeout=timeout, **kwargs
            )

        err_msg = f"Expected a file-like object, a path object or string, or a list of dicts; got {type(data).__name__}"
        raise TypeError(err_msg)


class GeographyResult(Dict):
    """Wrapper for geography objects returned by the Census Geocoding API."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Initialize the GeographyResult with the given data."""
        self.input: str | int | float | list | dict = data["result"].get("input", {})
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


class AddressResult(List):
    """Wrapper for address objects returned by the Census Geocoding API."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Initialize the AddressResult with the given data."""
        self.input: str | int | float | list | dict = data["result"].get("input", {})
        super().__init__(data["result"]["addressMatches"])
