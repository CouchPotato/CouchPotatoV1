'''
Created on 31.07.2010

@author: Christian
'''
from app.config.wrapper import Wrapper
from app.core.environment import Environment as env_
import os

class Bones(object):
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
            cf[name] = Wrapper(filename)
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

    def getPluginMgr(self):
        return env_.get('pluginManager')

class Description:
    def __init__(self):
        name = None
        author = None
        description = None
        version = None
        email = None
        logo = None
        www = None

    def fromConfig(self, config):
        attrs = (
                 'name', 'author',
                 'description', 'version',
                 'email', 'logo', 'www'
        )
        for attr in attrs:
            if config.has('info', attr):
                setattr(self, attr, config.get('info', attr))
