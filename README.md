Census Geocode
--------------

Census Geocode is a light weight Python wrapper for the US Census [Geocoder API](http://geocoding.geo.census.gov/geocoder/), compatible with both Python 2 and 3. It comes packaged with a simple command line tool for geocoding an address to a longitude and latitude, or a batch file into a parsed address and coordinates.

It's strongly recommended to review the [Census Geocoder docs](https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.pdf) before using this module.

Basic example:

```python
import censusgeocode as cg

cg.coordinates(x=-76, y=41)
cg.onelineaddress('1600 Pennsylvania Avenue, Washington, DC')
cg.address('1600 Pennsylvania Avenue', city='Washington', state='DC', zipcode='22052')
cg.addressbatch('data/addresses.csv')
```

Use the returntype keyword to specify 'locations' or 'geographies'. 'Locations' yields structured information about the address, and 'geographies' yields information about the Census geographies. Geographies is the default.
```python
cg.onelineaddress('1600 Pennsylvania Avenue, Washington, DC', returntype='locations')
```

Queries return a CensusResult object, which is basically a Python list with an extra 'input' property, which the Census returns to tell you how they interpreted your request.

```python
>>> result = cg.coordinates(x=-76, y=41)
>>> result.input
{
    u'vintage': {
        u'vintageName': u'Current_Current',
        u'id': u'4',
        u'vintageDescription': u'Current Vintage - Current Benchmark',
        u'isDefault': True
    },
    u'benchmark': {
        u'benchmarkName': u'Public_AR_Current',
        u'id': u'4',
        u'isDefault': False,
        u'benchmarkDescription': u'Public Address Ranges - Current Benchmark'
    },
    u'location': {
        u'y': 41.0,
        u'x': -76.0
    }
}
>>> result
[{
    '2010 Census Blocks': [{
        'AREALAND': 1409023,
        'AREAWATER': 0,
        'BASENAME': '1045',
        'BLKGRP': '1',
        'BLOCK': '1045',
        'CENTLAT': '+40.9957436',
        'CENTLON': '-076.0089338',
        'COUNTY': '079',
        'FUNCSTAT': 'S',
        'GEOID': '420792166001045',
        'INTPTLAT': '+40.9957436',
        'INTPTLON': '-076.0089338',
        'LSADC': 'BK',
        'LWBLKTYP': 'L',
        'MTFCC': 'G5040',
        'NAME': 'Block 1045',
        'OBJECTID': 9940449,
        'OID': 210404020212114,
        'STATE': '42',
        'SUFFIX': '',
        'TRACT': '216600'
    }],
    'Census Tracts': [{
        'AREALAND': 86404594,
        'AREAWATER': 650526,
        'BASENAME': '2166',
        'CENTLAT': '+41.0361462',
        'CENTLON': '-075.9801252',
        'COUNTY': '079',
        'FUNCSTAT': 'S',
        'GEOID': '42079216600',
        'INTPTLAT': '+41.0379841',
        'INTPTLON': '-075.9743749',
        'LSADC': 'CT',
        'MTFCC': 'G5020',
        'NAME': 'Census Tract 2166',
        'OBJECTID': 61245,
        'OID': 20790277158250,
        'STATE': '42',
        'TRACT': '216600'
    }],
    'Counties': [{
        'AREALAND': 2305974186,
        'AREAWATER': 41240020,
        'BASENAME': 'Luzerne',
        'CENTLAT': '+41.1768961',
        'CENTLON': '-075.9890400',
        'COUNTY': '079',
        'COUNTYCC': 'H1',
        'COUNTYNS': '01209183',
        'FUNCSTAT': 'A',
        'GEOID': '42079',
        'INTPTLAT': '+41.1727868',
        'INTPTLON': '-075.9760345',
        'LSADC': '06',
        'MTFCC': 'G4020',
        'NAME': 'Luzerne County',
        'OBJECTID': 866,
        'OID': 27590277115518,
        'STATE': '42'
    }],
    'States': [{
        'AREALAND': 115884236236,
        'AREAWATER': 3395797284,
        'BASENAME': 'Pennsylvania',
        'CENTLAT': '+40.9011252',
        'CENTLON': '-077.8369164',
        'DIVISION': '2',
        'FUNCSTAT': 'A',
        'GEOID': '42',
        'INTPTLAT': '+40.9024957',
        'INTPTLON': '-077.8334514',
        'LSADC': '00',
        'MTFCC': 'G4000',
        'NAME': 'Pennsylvania',
        'OBJECTID': 37,
        'OID': 27490163788605,
        'REGION': '1',
        'STATE': '42',
        'STATENS': '01779798',
        'STUSAB': 'PA'
    }]
}]
```

### Advanced

By default, the geocoder uses the "Current" vintage and benchmarks. To use another vintage or benchmark, use the `CensusGeocode` class:
````python
import censusgeocode
cg = censusgeocode.CensusGeocode(benchmark='Public_AR_Census2010', vintage='Census2010_Census2010')
cg.onelineaddress(foobar)
````

The Census may update the available benchmarks and vintages. Review the Census Geocoder docs for the currently available [benchmarks](https://geocoding.geo.census.gov/geocoder/benchmarks) and [vintages](https://geocoding.geo.census.gov/geocoder/vintages?form).

## Command line tool

The `censusgeocode` tool has two settings.

At the simplest, it takes one argument, an address, and returns a comma-delimited longitude, latitude pair.
````bash
censusgeocode '100 Fifth Avenue, New York, NY'
-73.992195,40.73797

censusgeocode '1600 Pennsylvania Avenue, Washington DC'
-77.03535,38.898754
````

The Census geocoder is reasonably good at recognizing non-standard addresses.
````bash
censusgeocode 'Hollywood & Vine, LA, CA'
-118.32668,34.101624
````

It can also use the Census Geocoder's batch function to process an entire file. The file must be comma-delimited, have no header, and include the following columns:
````
unique id, street address, state, city, zip code
````

The geocoder can read from a file:
````
censusgeocode --csv tests/fixtures/batch.csv
````
([example file](https://github.com/fitnr/censusgeocode/blob/master/tests/fixtures/batch.csv))

Or from stdin, using `-` as the filename:
````
cat tests/fixtures/batch.csv | censusgeocode --csv -
````

According to the Census docs, the batch geocoder is limited to 1000 rows.

The output will be a CSV file (with a header) and the columns:
* id
* address
* match
* matchtype
* parsed
* tigerlineid
* side
* lat
* lon

If your data doesn't have a unique id, try adding line numbers with the Unix command line utility `nl`:
```
nl -s , input.csv | censusgeocode --csv - > output.csv
```

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see http://www.gnu.org/licenses/.
