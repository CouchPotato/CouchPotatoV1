from app.config.wrapper import Wrapper
from app.core import getLogger
from app.core.controller import BasicController
from app.core.environment import Environment as env_
from app.lib.event import Event
from copy import copy
from mako.lookup import TemplateLookup
import os
import urllib
import cherrypy
from app.lib import dependencies
import traceback

log = getLogger(__name__)

### TEMP @todo: Integrate with classes.
def redirect(url):
    raise cherrypy.HTTPRedirect(url)
### /TEMP

class PluginController(BasicController):
    def __init__(self, plugin):
        self.plugin = plugin

    def _getPlugin(self, name):
        return env_.get('_pluginMgr').getPlugin(name)

class PluginBones(object):
    '''
    This class handles the loading of plugin-defined configuration files.
    '''
    def __init__(self, name, pluginMgr, path, package, *args, **kwargs):
        self.name = name
        self._info = None
        self._package = package
        self._about = About(self._getAbout())
        self._configFiles = dict()
        self._configPath = os.path.join('plugins', name)
        self._env = env_
        self._pluginMgr = pluginMgr
        self._pluginPath = path
        self._uuid = self._identify()
        self._exports = {}
        self._import = ImportLookup(self)
        """Holds the types that this plugin exports"""

        self._url = Url(self)
        self.postConstruct()
        self._applyStaticDirs()

    def _getDependencies(self):
        raise RuntimeError("Plugin does not specify dependencies")

    def checkDependencies(self):
        self._deps = dependencies.Dependencies(self._getDependencies()).asObject()

    def _export(self, *args, **kwargs):
        """Export types for other plugins"""
        if args: log.info("Ignored wargs in _import: %s" % self.name)

        for type_name, a_type in kwargs.iteritems():
            if isinstance(a_type, type):
                if type_name not in self._exports:
                    self._exports[type_name] = a_type
                else:
                    raise RuntimeError("Already exporting a type with name: %s" % type_name)
            else:
                raise RuntimeError("Not a type: %s" % a_type)

    def postConstruct(self):
        """Stub that is invoked after constructor."""
        pass
    def init(self):
        """Stub that is invoked once all plugins have been loaded."""
        pass

    def _identify(self):
        raise RuntimeError("Plugin must provide UUID")

    def _loadConfig(self, name):
        cf = self._configFiles
        if cf.has_key(name):
            return cf[name]

        filename = os.path.join(self._configPath, name)
        try:
            cf[name] = Wrapper(filename)
        except:
            log.info('Failed to load config: ' + str(filename) + "\n" + traceback.format_exc())
            pass

    def _loadConfigSet(self, nameSet):
        for name in nameSet:
            self._loadConfig(name)

    def _getConfig(self, name, builder = None):
        if self._configFiles.has_key(name):
            return self._configFiles[name]
        raise Exception('Config inexistent.')

    def _getPluginMgr(self):
        return env_.get('pluginManager')

    def _getAbout(self):
        return {}

    def _fire(self, name, *args, **kwargs):
        return self._fireCustom(Event, name, *args, **kwargs)

    def _getDbSession(self):
        return env_.get('db').createSession()

    def _fireCustom(self, EventType, *args, **kwargs):
        event = EventType(self, *args, **kwargs)
        return self._pluginMgr.fire(event)

    def _listen(self, to, callback, config = None, position = -1):
        self._pluginMgr.listen(to, callback, config, position)

    def _createController(self, ControllerType = PluginController):
        return ControllerType(self)

    def _upgradeDatabase(self, latest_version, scope):
        '''Call this to automatically upgrade your tables'''
        env_.get('db').upgradeDatabase(self._info, latest_version, scope)

    def _applyStaticDirs(self):
        if os.path.isdir(self._getStaticDir()):
            env_.get('frontend').registerStaticDir(
                            '/' + self._getVirtual(['static']), # /virtualPathNoLeadingSlash
                            self._getStaticDir()
        )
        self._env.get('frontend').registerStaticDir(
            '/' + self._getVirtual(['cache'])
            , self._getCacheDir()
        )

    def _getStaticDir(self, subdirectories = ()):
        dir = os.path.join(
            self._pluginPath,
            'static',
            *subdirectories
        )
        try:
            os.makedirs(dir)
        except Exception:
            pass
        return dir

    def _getCacheDir(self, subdirectories = ()):
        dir = os.path.join(
            self._env._dataDir,
            'cache',
            str(self._uuid),
            *subdirectories
        )
        try:
            os.makedirs(dir)
        except Exception:
            pass
        return dir

    def _getVirtual(self, subdirectories = None):
        subdirectories = subdirectories or []
        return '/'.join([
            '_plugins',
            self.name + '-' + str(self._uuid),
            ] + subdirectories
        )

    def _generateUrl(self):
        return '_plugins/' + self.name + '-' + str(self._uuid)

class About(object):
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

class Url(object):
    def __init__(self, plugin):
        self._plugin = plugin
        self._baseUrl = plugin._generateUrl()

    def __call__(self, *args, **kwargs):
        """
        Generate a plugin specific URL and adding custom
        parameters to it automatically.
        
        Explicitely use a trailing slash by setting
        _trailing to True
        """
        _trailing = kwargs.get('_trailing', False)
        result = self._baseUrl
        result += '/' + '/'.join(args) if args else ""
        result += '/' if _trailing else ""
        params = urllib.urlencode(kwargs)
        result += '?' + params if params else ""

        return result

    def __str__(self):
        return self()

class ImportLookup():
    def __init__(self, owner):
        self._owner = owner
        self._wrappers = {}
    def __getattr__(self, name):
        if not name in self._wrappers:
            self._wrappers[name] = DependencyImportWrapper(getattr(self._owner._deps, name))
        return self._wrappers[name]

class DependencyImportWrapper(object):
    def __init__(self, plugin):
        self._plugin = plugin

    def __getattr__(self, name):
        return self._plugin._exports[name]
