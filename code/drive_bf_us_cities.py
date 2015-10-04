#!/usr/bin/env python

"""
PURPOSE:

To scrape all the bf data for all US cities with more than 100k people.

Created on 2015-09-22T21:29:50
"""

from __future__ import division, print_function
import sys
import datetime
import argparse
import pandas as pd
import splinter_scrape_bf as ssbf


__author__ = "Matt Giguere (github: @mattgiguere)"
__license__ = "MIT"
__version__ = '0.0.1'
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"


def drive_bf_us_cities(num_cities=5, run_scraper=True, starting_city=''):
    """PURPOSE:
    To read in the US cities and add the bf results
    to the DB.
    """

    csf = pd.read_csv('../data/us_cities_over_100k.txt',
                      names=['city', 'state'], delimiter=' ')


    print('num_cities is {}'.format(num_cities))
    if num_cities is not 'all':
        num_cities = int(num_cities)
    else:
        num_cities = len(csf)

    if starting_city is not '':
        num_cities += csf[csf['city'] == starting_city[:-3]].index.values[0]

    if num_cities != 'all':
        cs = csf.head(int(num_cities))
    else:
        cs = csf

    # set pass_starting_city to False if it is not the default empty string:
    if starting_city is not '':
        pass_starting_city = False
    else:
        pass_starting_city = True

    for row_index, row in cs.iterrows():
        print('{}, {}'.format(row['city'], row['state']))
        print(datetime.datetime.now())
        if starting_city is not '' and row['city']+'_'+row['state'] == starting_city:
            pass_starting_city = True

        if pass_starting_city:
            print('Thundercats GO!!!')

        if run_scraper and pass_starting_city:
            ssbf.splinter_scrape_bf(row['city'], row['state'])
    print(datetime.datetime.now())


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
    parser.add_argument(
        '-s', '--starting_city',
        help='Specify a city to start on. Otherwise, drive_bf_us_cities will ' +
        'start with the first one in the list (new york). The format should ' +
        'be city_state (e.g. san_francisco_ca', default='')
    if len(sys.argv) > 7:
        print('use the command')
        print('python drive_bf_us_cities.py --num_cities all --run_scraper')
        sys.exit(2)

    args = parser.parse_args()

    drive_bf_us_cities(num_cities=args.num_cities,
                       run_scraper=args.run_scraper,
                       starting_city=args.starting_city)
