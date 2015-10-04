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
        print('Address not found'.format(args.address), file=sys.stderr)

if __name__ == '__main__':
    main()
