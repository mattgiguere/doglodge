#!/usr/bin/env python

"""
Created on 2015-09-26T12:13:49
"""

from __future__ import division, print_function
import sys
import argparse

try:
    import numpy as np
except ImportError:
    print('You need numpy installed')
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
except ImportError:
    print('You need to install matplotlib')

import pandas as pd

__author__ = "Matt Giguere (github: @mattgiguere)"
__license__ = "MIT"
__version__ = '0.0.1'
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"


def splinter_scrape_ta(arg1, arg2):
    """PURPOSE: To """


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

    splinter_scrape_ta(int(args.arg1), args.arg2)
