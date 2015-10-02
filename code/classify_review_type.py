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
    cmd = "SELECT review_text FROM ta_reviews"
    tadf = pd.read_sql_query(cmd, engine)
    return tadf


def classify_review_type(arg1, arg2):
    """PURPOSE: To """
    engine = cadb.connect_aws_db(write_unicode=True)

    # get the bringfido reviews
    bfdf = get_bf_reviews(engine)

    # get the ta reviews
    tadf = get_ta_reviews(engine)

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='argparse object.')
    parser.add_argument(
        'arg1',
        help='This argument does something.')
    parser.add_argument(
        'arg2',
        help='This argument does something else. By specifying ' +
             'the "nargs=>" makes this argument not required.',
             nargs='?')
    if len(sys.argv) > 3:
        print('use the command')
        print('python filename.py tablenum columnnum')
        sys.exit(2)

    args = parser.parse_args()

    classify_review_type(int(args.arg1), args.arg2)
