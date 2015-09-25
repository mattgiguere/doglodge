#!/usr/bin/env python

"""
Created on 2015-09-18T11:19:45
"""

from __future__ import division, print_function
import sys
import argparse
from time import time

try:
    import numpy as np
except ImportError:
    print('You need numpy installed')
    sys.exit(1)

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestCentroid
import connect_aws_db as cadb

reload(sys)
sys.setdefaultencoding('utf8')

__author__ = "Matt Giguere (github: @mattgiguere)"
__license__ = "MIT"
__version__ = '0.0.1'
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"


def create_and_train_model(engine):
    cmd = "SELECT review_rating, review_text FROM bf_reviews"
    bfdf = pd.read_sql_query(cmd, engine)
    bfdfl = bfdf[bfdf['review_text'].str.len() > 350].copy()
    train_data = bfdfl['review_text'].values[:1000]
    y_train = bfdfl['review_rating'].values[:1000]

    t0 = time()
    vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,
                                 stop_words='english')
    X_train = vectorizer.fit_transform(train_data)
    duration = time() - t0
    print('vectorized in {:.2f} seconds.'.format(duration))
    print(X_train.shape)

    clf = NearestCentroid()
    clf.fit(X_train, y_train)
    return clf, vectorizer


def retrieve_best_hotels2(city, state=''):
    """PURPOSE: To """
    city = str(city).lower()

    engine = cadb.connect_aws_db(write_unicode=True)

    # create and train the model to use to classify ratings:
    clf, vectorizer = create_and_train_model(engine)

    # read in the review data:
    cmd = "SELECT * FROM yelp_reviews WHERE review_category = 'dog'"
    yelp_reviews = pd.read_sql(cmd, engine)

    # now read in the hotel data:
    cmd = "SELECT * FROM yelp_hotels WHERE hotel_city='" + city + "'"
    yelp_hotels = pd.read_sql(cmd, engine)

    # join the two DataFrames:
    yelp = pd.merge(yelp_hotels, yelp_reviews, on='business_id', how='inner')

    yelp_review_text = yelp['review_text'].values
    print('Number of reviews: {}'.format(len(yelp_review_text)))

    t0 = time()
    X_pred = vectorizer.transform(yelp_review_text)
    duration = time() - t0
    print('transformed test data in {:.2f} seconds.'.format(duration))

    #yelp_city = yelp[yelp['hotel_city'] == city.strip()]

    #yelp_dog_review = yelp_city[yelp_city['review_text'].str.contains('dog')].copy().reset_index()

    #average_dog_ratings = [np.mean(yelp_dog_review[yelp_dog_review['hotel_id'] == hotel_id]['review_rating'].values) for hotel_id in np.unique(yelp_dog_review['hotel_id'])]

    #now predict the rating based on the sentiment of the review:
    y_pred = clf.predict(X_pred)
    yelp['dog_rating'] = y_pred

    # get the unique hotels
    unique_biz_ids = np.unique(yelp['business_id'])

    unique_hotel_df = yelp[yelp['business_id'].isin(unique_biz_ids)].copy()

    unique_hotel_df.drop_duplicates(cols='business_id', inplace=True)

    unique_hotel_df['average_dog_rating'] = [np.mean(yelp[yelp['business_id'] == business_id]['dog_rating'].values) for business_id in unique_hotel_df['business_id'].values]

    best_dog_hotel_names = unique_hotel_df.sort(columns='average_dog_rating', ascending=False)['hotel_name'].head(10).values

    best_dog_hotel_ratings = np.round(unique_hotel_df.sort(columns='average_dog_rating', ascending=False)['average_dog_rating'].head(10).values, 1)

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
