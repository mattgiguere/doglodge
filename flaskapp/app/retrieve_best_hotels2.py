#!/usr/bin/env python

"""
Created on 2015-09-18T11:19:45
"""

from __future__ import division, print_function
import sys
import argparse

try:
    import numpy as np
except ImportError:
    print('You need numpy installed')
    sys.exit(1)

import pandas as pd
import connect_aws_db as cadb

reload(sys)
sys.setdefaultencoding('utf8')

__author__ = "Matt Giguere (github: @mattgiguere)"
__license__ = "MIT"
__version__ = '0.0.1'
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"


def retrieve_best_hotels2(city, state=''):
    """PURPOSE: To """
    engine = cadb.connect_aws_db(write_unicode=True)
    cmd = 'SELECT * FROM yelp_reviews'

    yelp_reviews = pd.read_sql(cmd, engine)

    cmd = 'SELECT * FROM yelp_hotels'
    yelp_hotels = pd.read_sql(cmd, engine)
    yelp = pd.merge(yelp_hotels, yelp_reviews, on='business_id', how='inner')

    yelp_city = yelp[yelp['hotel_city'] == city.strip()]

    yelp_dog_review = yelp_city[yelp_city['review_text'].str.contains('dog')].copy().reset_index()

    average_dog_ratings = [np.mean(yelp_dog_review[yelp_dog_review['hotel_id'] == hotel_id]['review_rating'].values) for hotel_id in np.unique(yelp_dog_review['hotel_id'])]

    unique_hotels = yelp_dog_review[yelp_dog_review['hotel_id'].isin(np.unique(yelp_dog_review['hotel_id']))].copy()

    unique_hotels.drop_duplicates(cols='hotel_id', inplace=True)

    unique_hotels['average_rating'] = average_dog_ratings

    best_dog_hotel_names = unique_hotels.sort(columns='average_rating', ascending=False)['hotel_name'].head(10).values

    best_dog_hotel_ratings = np.round(unique_hotels.sort(columns='average_rating', ascending=False)['average_rating'].head(10).values, 1)

    string_ratings = [str(rat) for rat in best_dog_hotel_ratings]

    #print('best dog hotels:')
    #print(best_dog_hotel_names)

    return best_dog_hotel_names, string_ratings


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='argparse object.')
    parser.add_argument(
        'city',
        help='The name of the destination city.')
    parser.add_argument(
        'state',
        help='The name of the destination state ' +
             '(optional).', default='',
             nargs='?')
    if len(sys.argv) > 3:
        print('use the command')
        print('python retrieve_best_hotels.py Phoenix AZ')
        sys.exit(2)

    args = parser.parse_args()

    retrieve_best_hotels2(args.city, args.state)
