import sys
import os
sys.path.insert(0, '/var/www/html/doglodge.io')
sys.path.append('/home/ec2-user/anaconda/lib/python2.7/site-packages/')
os.environ['CredDir'] = '/home/ec2-user/'


print(sys.version)
print(sys.path)

from flaskapp import app as application