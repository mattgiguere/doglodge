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
    bfdfl = bfdf[bfdf['review_text'].str.len() > 300].copy()
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


def get_ta_reviews(city, engine, remove_shorts=True):
    # restore the bringfido reviews
    cmd = "SELECT h.hotel_url, h.hotel_img_url, h.business_id, "
    cmd += "h.hotel_name, h.hotel_price, r.review_text "
    cmd += "FROM ta_reviews r INNER JOIN ta_hotels h "
    cmd += "ON h.business_id=r.business_id "
    cmd += "WHERE h.hotel_city='" + city + "';"
    tadf = pd.read_sql_query(cmd, engine)
    if remove_shorts:
        tadf = tadf[tadf['review_text'].str.len() > 300].copy()
    return tadf


def get_yelp_reviews(city, engine, remove_shorts=True):
    # restore the bringfido reviews
    cmd = "SELECT h.business_id, h.hotel_name, r.review_text "
    cmd += "FROM yelp_reviews r INNER JOIN yelp_hotels h "
    cmd += "ON r.business_id=h.business_id "
    cmd += "WHERE h.hotel_city='" + city + "';"
    ydf = pd.read_sql_query(cmd, engine)
    if remove_shorts:
        ydf = ydf[ydf['review_text'].str.len() > 300].copy()
    return ydf


def retrieve_best_hotels2(city, state='',
                          revdb='ta',
                          max_revs=10):
    """PURPOSE: To """
    city = str(city).lower()

    engine = cadb.connect_aws_db(write_unicode=True)

    # create and train the model to use to classify ratings:
    clf, vectorizer = create_and_train_model(engine)

    if revdb == 'yelp':
        revdf = get_yelp_reviews(city, engine)
    if revdb == 'ta':
        revdf = get_ta_reviews(city, engine)

    review_text = revdf['review_text'].values
    print('Number of reviews: {}'.format(len(review_text)))

    t0 = time()
    X_pred = vectorizer.transform(review_text)
    duration = time() - t0
    print('transformed test data in {:.2f} seconds.'.format(duration))

    #yelp_city = yelp[yelp['hotel_city'] == city.strip()]

    #yelp_dog_review = yelp_city[yelp_city['review_text'].str.contains('dog')].copy().reset_index()

    #average_dog_ratings = [np.mean(yelp_dog_review[yelp_dog_review['hotel_id'] == hotel_id]['review_rating'].values) for hotel_id in np.unique(yelp_dog_review['hotel_id'])]

    #now predict the rating based on the sentiment of the review:
    y_pred = clf.predict(X_pred)
    revdf['dog_rating'] = y_pred

    # get the unique hotels
    unique_biz_ids = np.unique(revdf['business_id'])

    unique_hotel_df = revdf[revdf['business_id'].isin(unique_biz_ids)].copy()

    unique_hotel_df.drop_duplicates(cols='business_id', inplace=True)
    unique_hotel_df['num_dog_reviews'] = [len(revdf[revdf['business_id'] == business_id]) for business_id in unique_hotel_df['business_id'].values]
    #max_revs = unique_hotel_df['num_dog_reviews'].max()

    print('max reviews is: {}'.format(max_revs))

    unique_hotel_df['average_dog_rating'] = [np.mean(revdf[revdf['business_id'] == business_id]['dog_rating'].values) * 0.8 + min(1, unique_hotel_df[unique_hotel_df['business_id'] == business_id]['num_dog_reviews'].values[0]/max_revs) for business_id in unique_hotel_df['business_id'].values]

    print('dog ratings are...')
    print(unique_hotel_df['average_dog_rating'].values)

    uniq_df_srtd = unique_hotel_df.sort(columns='average_dog_rating', ascending=False).head(10).copy()

    best_dog_hotel_names = uniq_df_srtd['hotel_name'].values

    best_dog_hotel_ratings = np.round(uniq_df_srtd['average_dog_rating'].values, 1)

    string_ratings = [str(rat) for rat in best_dog_hotel_ratings]

    best_dog_hotel_imgs = uniq_df_srtd['hotel_img_url'].values
    best_dog_hotel_urls = uniq_df_srtd['hotel_url'].values
    best_dog_hotel_prices = [str(prc) if prc > 0 else "nan" for prc in np.int64(np.round(uniq_df_srtd['hotel_price'].values))]
    print('best dog hotel prices')
    print(best_dog_hotel_prices)
    #print('best dog hotels:')
    #print(best_dog_hotel_names)

    return best_dog_hotel_names, string_ratings, best_dog_hotel_imgs, best_dog_hotel_urls, best_dog_hotel_prices


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
