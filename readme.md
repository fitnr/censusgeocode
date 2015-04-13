Census Geocode
--------------

Python wrapper for the US Census [Geocoder API](http://geocoding.geo.census.gov/geocoder/).

Basic example

```python
from censusgeocode import CensusGeocode

cg = CensusGeocode()

cg.coordinates(x=-76, y=41)
cg.onelineaddress('1600 Pennsylvania Avenue, Washington, DC')
cg.address('1600 Pennsylvania Avenue', city='Washington', state='DC', zipcode='22052')
```

Use the returntype keyword to specify 'locations' or 'geographies'. Geographies is the default.
```python
cg.onelineaddress('1600 Pennsylvania Avenue, Washington, DC', returntype='locations')
```

Queries return a CensusResult object, which closely matches the raw result.
```python
result = cg.coordinates(x=-76, y=41)
result.geographies
{
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
}
```