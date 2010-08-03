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
from mako.lookup import TemplateLookup
from mako.template import Template
from app.core.controller import BasicController
from copy import copy

log = getLogger(__name__)

class PluginController(BasicController):
    def __init__(self, plugin, views, mako_lookup):
        self.plugin = plugin
        self.makoLookup = mako_lookup
        self.views = views
        self.static = os.path.join(views, 'static')
        env_.get('frontend').registerStaticDir(
                            self._getVirtual('static'),
                            self._getStaticDir()
        )#register static
        self.const = {
            'static' : self._getVirtual('static')
        }

    def render(self, name, vars = {}, *args, **kwargs):
        vars = copy(vars)
        vars.update(self.const)
        name = os.path.join(self.views, name)
        template = Template(filename = name, lookup = self.makoLookup)
        return template.render_unicode(vars, *args, **kwargs)

    def _getVirtual(self, subdirectories = ()):
        return os.path.join(
            '_plugins',
            self.plugin._info.name + '-' + str(self.plugin._info.version),
            *subdirectories
        )

    def _getStaticDir(self, subdirectories = ()):
        return os.path.join(
            self.plugin.pluginPath,
            'static',
            *subdirectories
        )

class PluginBones(object):
    '''
    This class handles the loading of plugin-defined configuration files.
    '''

    def __init__(self, name, pluginMgr, path = None, *args, **kwargs):
        '''
        Constructor
        '''
        self.name = name
        self.pluginPath = path
        self.pluginMgr = pluginMgr
        self.configPath = os.path.join('plugins', name)
        self.configFiles = dict()
        self.about = About(self.getAbout())
        self.postConstruct()
        if self.pluginPath:
            self.makoLookup = TemplateLookup(directories = [os.path.join(self.pluginPath, 'views')])

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

    def getAbout(self):
        return {}

    def _fire(self, name, input = None):
        self._fireCustom(Event, name, input)

    def _fireCustom(self, EventType, name, *args, **kwargs):
        event = EventType(self, name, *args, **kwargs)
        if env_.get('debug'):
            log.info('FIRING: ' + name)

        self.pluginMgr.fire(event)

    def _listen(self, to, callback, config = None, position = -1):
        self.pluginMgr.listen(to, callback, config, position)

    def createController(self, view_subfolders = (), ControllerType = PluginController):
        views_path = [self.pluginPath, 'views']
        views_path.extend(view_subfolders)
        views_path = os.path.join(*views_path)
        return ControllerType(self, views_path, self.makoLookup)


class About:
    def __init__(self, info_dict):
        self.name = None
        self.author = None
        self.description = None
        self.version = None
        self.email = None
        self.logo = None
        self.www = None
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
