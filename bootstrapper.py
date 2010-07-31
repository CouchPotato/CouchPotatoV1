'''
Created on 31.07.2010

@author: Christian
'''
from optparse import OptionParser
import sys
import os
import logging
import app
from app.CouchPotato import CouchPotato as cp_
from app.config.configApp import configApp 

def create_dir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)
        
def init_logging(base_path, target):
    app.configLogging(os.path.join(base_path, 'logging.conf'), target)
    return logging.getLogger(__name__)

p = OptionParser()
p.add_option('-d', action = "store_true",
             dest = 'daemonize', help = "Run the server as a daemon")
p.add_option('-q', '--quiet', action = "store_true",
             dest = 'quiet', help = "Don't log to console")
p.add_option('-p', '--pidfile',
             dest = 'pidfile', default = None,
             help = "Store the process id in the given file")

options, args = p.parse_args()

config = 'config/config.ini'
if args.__len__() == 1:
    config = args[0]
elif args.__len__() > 1:
    print ('Invalid argument cound: [config path]')
    sys.exit(1)

cp_.setBasePath(os.path.dirname(config))
config_name = os.path.basename(config)
#Load Configuration
try:
    ca = configApp(config_name)
    cp_.cfg = ca;
    
except Exception as e:
    print 'Could not initialize config. Check the path' + str(e) 
    sys.exit(1)

#create directories
create_dir(ca.get('paths', 'cache'))

cp_.log = log = init_logging(cp_.getBasePath(), ca.get('paths', 'logs'))
cp_.options = options
cp_.args = args
