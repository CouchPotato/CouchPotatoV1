'''
Created on 31.07.2010

@author: Christian
'''
from app.config.wrapper import Wrapper
from app.core.environment import Environment as env_
import os
from app.core import getLogger
import traceback
from app.lib.plugin.event import Event

log = getLogger(__name__)

class Bones(object):
    '''
    This class handles the loading of plugin-defined configuration files.
    '''

    def __init__(self, name, pluginMgr):
        '''
        Constructor
        '''
        self.name = name
        self.pluginMgr = pluginMgr
        self.configPath = os.path.join('plugins', name)
        self.configFiles = dict()
        self.info = Info(self.getInfo())
        self.postConstruct()

    def postConstruct(self):
        '''stub that is invoked after constructor'''
        pass
    def init(self):
        pass

    def loadConfig(self, name):
        cf = self.configFiles
        if cf.has_key(name):
            return cf[name]

        filename = os.path.join(self.configPath, name)
        try:
            cf[name] = Wrapper(filename)
        except:
            log.info('Failed to load config: ' + str(filename) + "\n" + traceback.format_exc())
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

    def getInfo(self):
        return {}

    def fire(self, name, data):
        event = Event(self, name, input)
        if env_.get('debug'):
            log.info('FIRING: ' + name)

        self.pluginMgr.fire(event)


class Info:
    def __init__(self, info_dict):
        name = None
        author = None
        description = None
        version = None
        email = None
        logo = None
        www = None
        self.fromDict(info_dict)

    def fromDict(self, dict):
        attrs = (
                 'name', 'author',
                 'description', 'version',
                 'email', 'logo', 'www'
        )
        for attr in attrs:
            if dict.has_key(attr):
                setattr(self, attr, dict[attr])
