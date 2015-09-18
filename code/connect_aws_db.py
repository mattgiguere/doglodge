#!/usr/bin/env python

"""
Created on 2015-04-04T11:28:18
"""

from __future__ import division, print_function
import sys
import subprocess
from sqlalchemy import create_engine

try:
    import pymysql
except ImportError:
    print('You need pymysql installed')
    sys.exit(1)

__author__ = "Matt Giguere (github: @mattgiguere)"
__license__ = "MIT"
__version__ = '0.0.1'
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = "Production"


def get_credentials_dir():
    """
    PURPOSE: A routine for pointing to the credentials directory.
    """
    cmd = 'echo $CredDir'
    #read in the CredDir string
    cdir = subprocess.check_output(cmd, shell=True)
    #chop off the newline character at the end
    cdir = cdir[0:len(cdir)-1]
    #and return it
    return cdir


def connect_aws_db(legacy=False, write_unicode=False):
    """PURPOSE:
    A function for connecting to the doglodge.io AWS RDS MySQL database.

    :param legacy: [optional]
        If legacy is set, a PyMySQL connection will be returned.
        Otherwise, a SQLAlchemy engine will be returned. This is
        to handle the deprecated MySQL connections in pandas.

    :param write_unicode: [optional]
        If set, text will be written to the MySQL DB as unicode.
    """

    #retrieve credentials:
    cdir = get_credentials_dir()
    credsf = open(cdir+'.credentials/SQL/cawsi', 'r')
    creds = credsf.read().split('\n')
    if legacy:
        conn = pymysql.connect(host=creds[0],
                               port=int(creds[1]),
                               user=creds[2],
                               passwd=creds[3],
                               db=creds[4])
        #cur = conn.cursor()
        return conn
    else:
        #example:
        #mysql+pymysql://<username>:<password>@<host>/<dbname>[?<options>]
        cmd = "mysql+pymysql://"
        cmd += creds[2]+':'
        cmd += creds[3]+'@'
        cmd += creds[0]+'/'
        cmd += creds[4]

        if write_unicode:
            cmd += '?charset=utf8'

        engine = create_engine(cmd)
        return engine

