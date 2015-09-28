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


def get_hotel_urls(city, state, engine):
    """Retrieve the hotels for the given city and state"""

    # manipulate the city string into the proper form
    citystr = (' ').join(city.lower().split('_'))
    cmd = "SELECT hotel_url FROM ta_hotels WHERE "
    cmd += "hotel_city='"+citystr+"' AND "
    cmd += "hotel_state='"+state.lower()+"'"
    result = engine.execute(cmd)
    return [row['hotel_url'] for row in result]


def splinter_scrape_ta_reviews(city='', state='', write_to_db=False):
    """PURPOSE: To """
    engine = cadb.connect_aws_db(write_unicode=True)

    links = get_hotel_urls(city, state, engine)
    usernames = []
    memberids = []
    locations = []
    titles = []
    ratings = []
    dates = []
    reviews = []
    review_ids = []

    columns = ['review_id',
               'hotel_id',
               'hotel_name',
               'business_id',
               'biz_review_id',
               'biz_member_id',
               'username',
               'review_title',
               'review_rating',
               'review_text',
               'review_date']

    bigdf = pd.DataFrame(columns=columns)

    url = links[idx]
    hotel_name = hotel_names[idx]

    more_reviews = True
    page = 1
    while more_reviews:
        #print('*'*50)
        print('*'*50)
        print('Now on page {}'.format(page))
        #print('*'*50)
        
        df = pd.DataFrame(columns=columns)

        ret_dict = return_results(url, page)
        print(ret_dict['locs'])
        print(ret_dict['ttls'])
        df['biz_review_id'] = ret_dict['revids']
        df['biz_member_id'] = ret_dict['mmbrids']
        df['username'] = ret_dict['usrnms']
        df['review_title'] = ret_dict['ttls']
        df['review_rating'] = ret_dict['rtngs']
        df['review_date'] = ret_dict['dts']
        df['review_text'] = ret_dict['rvws']
        df['hotel_name'] = hotel_name
        url = ret_dict['url']
        more_reviews = ret_dict['more_reviews']
        page = ret_dict['page']
        print('successfully completed page {}'.format(page))
        bigdf = bigdf.append(df)
        more_reviews = False



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
