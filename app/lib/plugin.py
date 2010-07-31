'''
Created on 31.07.2010

@author: Christian
'''
from app.config.configWrapper import ConfigWrapper
from app.CouchPotato import Environment as _env
import os

class Plugin(object):
    '''
    This class handles the loading of plugin-defined configuration files.
    '''

    def __init__(self, configPath):
        '''
        Constructor
        '''
        self.configPath = configPath
        self.configFiles = dict() 
        
    def loadConfig(self, name):
        cf = self.configFiles
        if cf.has_key(name):
            return cf[name]
        
        filename = os.path.join(self.configPath, name)
        try:
            cf[name] = ConfigWrapper(filename)
        except:
            _env.log.info('Failed to load config: ' + str(filename))
            pass
        
    def loadConfigSet(self, nameSet):
        for name in nameSet:
            self.loadConfig(name)
            
    def getConfig(self, name, builder = None):
        if self.configFiles.has_key(name):
            return self.configFiles[name]
        raise Exception('Config inexistent.')
