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
from sklearn.neighbors import NearestCentroid
from sklearn import metrics
import connect_aws_db as cadb


__author__ = "Matt Giguere (github: @mattgiguere)"
__license__ = "MIT"
__version__ = '0.0.1'
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"


def get_bf_reviews(engine):
    # restore the bringfido reviews
    cmd = "SELECT review_text FROM bf_reviews"
    bfdf = pd.read_sql_query(cmd, engine)
    return bfdf


def get_ta_reviews(engine):
    # restore the bringfido reviews
    cmd = "SELECT biz_review_id, review_text FROM ta_reviews"
    tadf = pd.read_sql_query(cmd, engine)
    return tadf


def update_table_rev_cat(df, engine):
    brids = df[df['review_category'] == 'dog']['biz_review_id'].values
    sbrids = [str(brid) for brid in brids]
    cmd = 'UPDATE ta_reviews SET review_category = "dog" '
    cmd += 'WHERE biz_review_id in ('+(',').join(sbrids)+')'

    conn = engine.connect()
    conn.execute(cmd)


def classify_review_type(db='ta', verbose=True):
    """PURPOSE: To """
    engine = cadb.connect_aws_db(write_unicode=True)

    if verbose:
            print('grabbing bf data...')
    # get the bringfido reviews
    bfdf = get_bf_reviews(engine)

    if db == 'ta':
        if verbose:
            print('grabbing ta data...')
        # get the ta reviews
        tadf = get_ta_reviews(engine)

    train_data = np.hstack((bfdf['review_text'].values[:1500],
                            tadf['review_text'].values[:1500]))

    labels = ['dog'] * 1500
    labels.extend(['general'] * 1500)
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

    X_yrevs = vectorizer.transform(tadf['review_text'].values)

    if verbose:
        print('predicting...')
    pred = clf.predict(X_yrevs)

    tadf['review_category'] = pred

    update_table_rev_cat(tadf, engine)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='argparse object.')
    parser.add_argument(
        'db',
        help='This argument specifies the database to update. ' +
             'the default is ta.',
             nargs='?', default='ta')
    if len(sys.argv) > 3:
        print('use the command')
        print('python classify_review_type.py ta')
        sys.exit(2)

    args = parser.parse_args()

    classify_review_type(db=args.db)
