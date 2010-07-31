'''
Created on 31.07.2010

@author: Christian
'''
from optparse import OptionParser
import sys
import os
import logging
import app
from app.CouchPotato import Environment as cp_
from app.config.configApp import appConfig

def create_dir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)

def init_logging(target, debug = False):
    app.configLogging(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'debug.conf' if debug else 'logging.conf'), target)
    return logging.getLogger(__name__)

p = OptionParser()
p.add_option('-d', action = "store_true",
             dest = 'daemonize', help = "Run the server as a daemon")
p.add_option('-q', '--quiet', action = "store_true",
             dest = 'quiet', help = "Don't log to console")
p.add_option('-p', '--pidfile',
             dest = 'pidfile', default = None,
             help = "Store the process id in the given file")
p.add_option('-t', '--debug', action = "store_true",
             dest = 'debug', help = "Run in debug mode")

options, args = p.parse_args()

config = 'data/config.ini'
if args.__len__() == 1:
    config = args[0]
elif args.__len__() > 1:
    print ('Invalid argument cound: [config path]')
    sys.exit(1)

cp_.setBasePath(os.path.dirname(config))
config_name = os.path.basename(config)
#Load Configuration
try:
    ca = appConfig(config_name)
    cp_.cfg = ca;

except Exception as e:
    print 'Could not initialize config. Check the path' + str(e)
    sys.exit(1)

#create directories
create_dir(ca.get('paths', 'cache'))

cp_.log = log = init_logging(ca.get('paths', 'logs'), options.debug)
cp_.options = options
cp_.args = args
