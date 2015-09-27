#!/usr/bin/env python

"""
Created on 2015-09-27T16:51:39
"""

from __future__ import division, print_function
import sys
import argparse
import re
import time
try:
    import numpy as np
except ImportError:
    print('You need numpy installed')
    sys.exit(1)
import pandas as pd
from splinter.browser import Browser
import connect_aws_db as cadb


__author__ = "Matt Giguere (github: @mattgiguere)"
__license__ = "MIT"
__version__ = '0.0.1'
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"


def splinter_scrape_ta_reviews(arg1, arg2):
    """PURPOSE: To """


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='argparse object.')
    parser.add_argument(
        '--city_url',
        help='The url of the city to scrape.',
        nargs='?', default='')
    parser.add_argument(
        '-c', '--city',
        help='The url of the city to scrape.',
        nargs='?', default='')
    parser.add_argument(
        '-s', '--state',
        help='This name of the state to scrape.',
             nargs='?', default='')
    parser.add_argument(
        '-w', '--write_to_db',
        help='Set if you want to write the results to the DB.',
             default=False, action='store_true')
    if len(sys.argv) > 7:
        print('use the command')
        print('python splinter_scrape_bf.py city state')
        print('For example:')
        print('python splinter_scrape_ta_reviews.py -c new_haven -s ct')
        sys.exit(2)

    args = parser.parse_args()

    splinter_scrape_ta_reviews(city=args.city, state=args.state, write_to_db=args.write_to_db)
