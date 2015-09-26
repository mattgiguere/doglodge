activate_this = '/var/www/html/doglodge.io/dog-env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
import os
sys.path.insert(0, '/var/www/html/doglodge.io')
sys.path.append('/home/ec2-user/anaconda/lib/python2.7/site-packages/')
os.environ['CredDir'] = '/home/wwwuser/.credentials/'

from flaskapp import app as application