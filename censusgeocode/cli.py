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
import argparse
from .censusgeocode import CensusGeocode
from . import __version__

def main():
    parser = argparse.ArgumentParser('censusgeocode')

    parser.add_argument('-v', '--version', action='version', version='%(prog)s v' + __version__)
    parser.add_argument('address', type=str)
    parser.add_argument('--timeout', metavar='SECONDS', type=int, default=12, help='Request timeout [default: 12]')

    args = parser.parse_args()

    gc = CensusGeocode()
    result = gc.onelineaddress(args.address, timeout=args.timeout)

    try:
        print('{}, {}'.format(result[0]['coordinates']['x'], result[0]['coordinates']['y']))

    except IndexError:
        print('Address not found'.format(args.address), file=sys.stderr)

if __name__ == '__main__':
    main()
