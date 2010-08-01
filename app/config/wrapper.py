'''
Created on 31.07.2010

@author: Christian
'''
import ConfigParser
from app.core.environment import Environment as env_
import os
import logging

log = logging.getLogger(__name__)

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
        file = os.path.join(env_.get('dataDir'), 'config', file)
        self._initDirectory(file)
        try:
            self.file = file
            self.p = ConfigParser.RawConfigParser()
            self.p.read(self.file)
            if hasattr(self, 'initConfig'):
                self.initConfig()
            if hasattr(onLoad, '__call__'):
                onLoad(self)
        except Exception as e:
            log.info('Error while loading configuration.')
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

    def parser(self):
        return self.p

    def sections(self):
        return self.s

    def set(self, section, option, value):
        return self.p.set(section, option, value)

    def get(self, section, option):
        value = self.p.get(section, option)
        if str(value).lower() in self.bool:
            return self.bool.get(str(value).lower())
        return value

    def _initDirectory(self, filename):
        directory = os.path.dirname(filename)
        if not os.path.isdir(directory):
            os.mkdir(directory)
