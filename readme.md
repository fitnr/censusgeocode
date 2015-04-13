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

Add queries will return a CensusResult object, which closely matches the raw result.
