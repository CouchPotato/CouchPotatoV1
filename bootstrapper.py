'''
Created on 31.07.2010

@author: Christian
'''
from optparse import OptionParser
import sys
import os
import logging
import app
from app.CouchPotato import Environment as _env
from app.config.configApp import Global

def create_dir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)




#create directories
create_dir(ca.get('paths', 'cache'))

_env.log = log = init_logging(ca.get('paths', 'logs'), options.debug)
_env.options = options
_env.args = args
