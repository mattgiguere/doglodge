#!/usr/bin/env python

"""
Created on 2015-10-02T10:10:24
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
from time import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
# from sklearn.neighbors import NearestCentroid
# from sklearn import metrics
import connect_aws_db as cadb


__author__ = "Matt Giguere (github: @mattgiguere)"
__license__ = "MIT"
__version__ = '0.0.1'
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"


def reset_review_cats(engine):
    """
    PURPOSE:
    To set all the review categories in the ta_reviews table
    back to NULL.
    """
    cmd = 'UPDATE ta_reviews set review_category=NULL;'

    conn = engine.connect()
    conn.execute(cmd)


def get_bf_reviews(engine, remove_shorts=True):
    # restore the bringfido reviews
    cmd = "SELECT review_text FROM bf_reviews"
    bfdf = pd.read_sql_query(cmd, engine)
    if remove_shorts:
        bfdf = bfdf[bfdf['review_text'].str.len() > 300].copy()
    return bfdf


def get_ta_reviews(engine, remove_shorts=True):
    # restore the bringfido reviews
    cmd = "SELECT biz_review_id, review_text FROM ta_reviews"
    tadf = pd.read_sql_query(cmd, engine)
    if remove_shorts:
        tadf = tadf[tadf['review_text'].str.len() > 300].copy()
    return tadf


def get_yelp_reviews(engine, remove_shorts=True):
    # restore the bringfido reviews
    cmd = "SELECT yelp_review_id, review_text FROM yelp_reviews"
    ydf = pd.read_sql_query(cmd, engine)
    if remove_shorts:
        ydf = ydf[ydf['review_text'].str.len() > 300].copy()
    return ydf


def update_table_rev_cat(df, engine):
    brids = df[df['review_category'] == 'dog']['biz_review_id'].values
    sbrids = [str(brid) for brid in brids]
    cmd = 'UPDATE ta_reviews SET review_category = "dog" '
    cmd += 'WHERE biz_review_id in ('+(',').join(sbrids)+')'

    conn = engine.connect()
    conn.execute(cmd)


def classify_review_type(traindb='yelp', ntrain_dog_revs=1500,
                         ntrain_gen_revs=1500, classdb='ta', verbose=False):
    """
    PURPOSE: To classify reviews as being either pet-related or general.

    :param traindb:
    The data set to use for training. The default is Yelp.

    :param ntrain_dog_revs:
    The number of dog-related hotel reviews to use in the training.

    :param ntrain_gen_revs:
    The number of general hotel reviews to use in the training.

    :param classdb:
    The data set to classify (either yelp or ta)

    :param verbose:
    Set this to True to print progress shit.
    """
    engine = cadb.connect_aws_db(write_unicode=True)

    if verbose:
            print('grabbing bf data...')
    # get the bringfido reviews
    bfdf = get_bf_reviews(engine)

    if verbose:
        print('grabbing general review data...')
    if traindb == 'ta':
        print('using TA data for training...')
        gentraindf = get_ta_reviews(engine)
    if traindb == 'yelp':
        print('using Yelp data for training...')
        gentraindf = get_yelp_reviews(engine)

    train_data = np.hstack((bfdf['review_text'].values[:ntrain_dog_revs],
                            gentraindf['review_text'].values[:ntrain_gen_revs]))

    labels = ['dog'] * ntrain_dog_revs
    labels.extend(['general'] * ntrain_gen_revs)
    y_train = labels

    if verbose:
        print('vectorizing...')
    t0 = time()
    vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,
                                 stop_words='english')
    X_train = vectorizer.fit_transform(train_data)
    duration = time() - t0
    print('vectorized in {:.2f} seconds.'.format(duration))

    penalty = 'l2'
    clf = LinearSVC(loss='l2', penalty=penalty, dual=False, tol=1e-3)

    if verbose:
        print('training model...')
    clf.fit(X_train, y_train)

    if classdb == 'yelp':
        print('categorizing Yelp data...')
        classdf = get_yelp_reviews(engine, remove_shorts=False)
    if classdb == 'ta':
        print('categorizing TA data...')
        classdf = get_ta_reviews(engine, remove_shorts=False)

    X_yrevs = vectorizer.transform(classdf['review_text'].values)

    if verbose:
        print('predicting...')
    pred = clf.predict(X_yrevs)

    classdf['review_category'] = pred

    update_table_rev_cat(classdf, engine)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='argparse object.')
    parser.add_argument(
        '-t', '--traindb',
        help='This argument specifies the database to use for training. ' +
             'the default is yelp.',
             default='yelp')
    parser.add_argument(
        '--ntrain_dog_revs',
        help='This argument specifies the number of dog-related reviews ' +
             'to use for training.',
             default=1500, type=int)
    parser.add_argument(
        '-c', '--classdb',
        help='This argument specifies the database to classify. ' +
             'the default is ta.',
             default='ta')
    parser.add_argument(
        '--ntrain_gen_revs',
        help='This argument specifies the number of general hotel reviews ' +
             'to use for training.',
             default=1500, type=int)
    parser.add_argument(
        '-v', '--verbose',
        help='Print more shit.',
             action='store_true')
    if len(sys.argv) > 11:
        print('use the command')
        print('python classify_review_type.py -t yelp -c ta --verbose')
        sys.exit(2)

    args = parser.parse_args()

    classify_review_type(traindb=args.traindb,
                         ntrain_dog_revs=args.ntrain_dog_revs,
                         classdb=args.classdb,
                         ntrain_gen_revs=args.ntrain_gen_revs,
                         verbose=args.verbose)
