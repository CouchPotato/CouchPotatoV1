'''
Created on 31.07.2010

@author: Christian
'''
import ConfigParser
from app.core.environment import Environment as _env
import os

class Wrapper(object):
    '''
    This class wraps a configuration file
    '''


    def __init__(self, file, onLoad = None):
        '''
        Load config file or return false.
        The parameter onLoad is used to run the method against
        the newly created config self.
        '''
        file = os.path.join(_env.getBasePath(), file)
        try:
            self.file = file
            self.p = ConfigParser.RawConfigParser()
            self.p.read(self.file)
            self.initConfig()
            if hasattr(onLoad, '__call__'):
                onLoad(self)
        except Exception as e:
            _env.log.info('Error while loading configuration.')
            raise

    def save(self):
        with open(self.file, 'wb') as configfile:
            self.p.write(configfile)

    def addSection(self, section):
        if not self.p.has_section(section):
            self.p.add_section(section)

    def setDefault(self, section, option, value):
        if not self.p.has_option(section, option):
            self.p.set(section, option, value)
