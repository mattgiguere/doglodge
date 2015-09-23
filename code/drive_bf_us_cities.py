#!/usr/bin/env python

"""
PURPOSE:

To scrape all the bf data for all US cities with more than 100k people.

Created on 2015-09-22T21:29:50
"""

from __future__ import division, print_function
import sys
import argparse
import splinter_scrape_bf as ssbf

try:
    import numpy as np
except ImportError:
    print('You need numpy installed')
    sys.exit(1)

import pandas as pd

__author__ = "Matt Giguere (github: @mattgiguere)"
__license__ = "MIT"
__version__ = '0.0.1'
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"


def drive_bf_us_cities(num_cities=5, run_scraper=True):
    """PURPOSE:
    To read in the US cities and add the bf results
    to the DB.
    """
    csf = pd.read_csv('../data/us_cities_over_100k.txt',
                      names=['city', 'state'], delimiter=' ')

    if num_cities != 'all':
        cs = csf.head(int(num_cities))
    else:
        cs = csf
    for row_index, row in cs.iterrows():
        print('{}, {}'.format(row['city'], row['state']))
        if run_scraper:
            ssbf.splinter_scrape_bf(row['city'], row['state'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='argparse object.')
    parser.add_argument(
        '-n', '--num_cities',
        help='The number of cities to add to the db. ' +
             'The default is the five most populous cities.',
             nargs='?', default=5)
    parser.add_argument(
        '-r', '--run_scraper',
        help='If run_scraper is set, this code runs splinter_scrape_bf. ' +
             'Otherwise, it simply prints out the city and state.',
             action='store_true', default=False)
    if len(sys.argv) > 5:
        print('use the command')
        print('python drive_bf_us_cities.py --num_cities all --run_scraper')
        sys.exit(2)

    args = parser.parse_args()

    drive_bf_us_cities(num_cities=args.num_cities, run_scraper=args.run_scraper)
