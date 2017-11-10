#!/usr/bin/env python3
# Copyright (C) 2015-7 Neil Freeman

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
from __future__ import print_function
import sys
import io
import csv
import argparse
from .censusgeocode import CensusGeocode
from . import __version__


rettype = 'locations'


def main():
    parser = argparse.ArgumentParser('censusgeocode')

    parser.add_argument('-v', '--version', action='version', version='%(prog)s v' + __version__)
    parser.add_argument('address', type=str, nargs='?', default=None)
    parser.add_argument('--csv', type=str, help=(
        'comma-delimited file of addresses. No header. '
        'Must have the following columns: id, street address, city, state, zip. '
        'id must be a unique. '
        'Read from stdin with -')
    )
    parser.add_argument('--timeout', metavar='SECONDS', type=int, default=12, help='Request timeout [default: 12]')

    args = parser.parse_args()
    cg = CensusGeocode()

    if args.address:
        result = cg.onelineaddress(args.address, returntype=rettype, timeout=args.timeout)

        try:
            print('{},{}'.format(result[0]['coordinates']['x'], result[0]['coordinates']['y']))

        except IndexError:
            print('Address not found'.format(args.address), file=sys.stderr)

    elif args.csv:
        if args.csv == '-':
            # No streaming here - consume the entirety of stdin.
            infile = io.StringIO()
            csv.writer(infile).writerows(csv.reader(sys.stdin))
            infile.seek(0)

        else:
            infile = args.csv

        result = cg.addressbatch(infile, returntype=rettype, timeout=args.timeout)

        fieldnames = cg.batchfields[rettype] + ['lat', 'lon']
        fieldnames.pop(fieldnames.index('coordinate'))
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)

    else:
        print('Address or csv file required')

if __name__ == '__main__':
    main()
