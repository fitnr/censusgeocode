# Copyright (C) 2015 Neil Freeman

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

def main():
    parser = argparse.ArgumentParser('censusgeocode')

    parser.add_argument('address', type=str)

    args = parser.parse_args()

    gc = CensusGeocode()
    result = gc.onelineaddress(args.address)

    try:
        print('{}, {}'.format(result[0]['coordinates']['x'], result[0]['coordinates']['y']))

    except IndexError:
        print('Address not found: {}'.format(args.address), file=sys.stderr)

if __name__ == '__main__':
    main()
