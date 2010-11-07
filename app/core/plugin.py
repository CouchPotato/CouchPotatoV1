from .environment import Environment as env_
from app.core import getLogger
from app.core.db import _tables
from app.lib.chain import Chain as PluginChain
from app.lib.event import Event
import os
import glob
import sys
import traceback
import uuid
log = getLogger(__name__)

class PluginLoader:
    def __init__(self):
        env_._pluginMgr = self
        self.pluginChains = {}
        self.pluginsByName = {}
        self.pluginsByModule = {}
        """Plugins by module names"""
        self.pluginsByUuid = {}
        self.pluginModules = {}
        self.pluginModuleNames = {}
        """Holds the plugin modules by UUID"""
        self.paths = {
                      'core' : ('app.plugins.', os.path.join(env_.get('appDir'), 'app', 'plugins')),
                      'user' : ('plugins.', os.path.join(env_.get('dataDir'), 'plugins'))
                      }
        for type, tuple in self.paths.iteritems():
            self.loadFromDir(type, tuple[0], tuple[1])

        if len(self.pluginsByName):
            log.info('Plugins loaded: ' + str(len(self.pluginsByName)))
            self.initPlugins()
        else:
            log.info('No pluginsByName have been loaded.')

    def loadFromDir(self, type, module, dir):
        """Load each directory as plugin."""
        for file in glob.glob(os.path.join(dir, '*')):
            plugin_name = os.path.basename(file)
            plugin_dir = os.path.join(dir, plugin_name)
            if os.path.isdir(plugin_dir):
                self.loadPlugin(type, module, plugin_name, plugin_dir)

    def loadPlugin(self, type, module, name, path):
        """Load individual directory as plugin."""
        module_name = module + name
        log.info('Loading plugin: ' + module + name)
        try:
            m = getattr(self.loadModule(module + name), name)
            self.registerPlugin(type, name, m, module_name, m.start(name, self, path, m))
        except:
            log.error("Failed loading plugin: " + name + "\n" + traceback.format_exc())

    def loadModule(self, name):
        """
        Load module by name.
        
        Log exception and reraise exception.
        """
        try:
            m = __import__(name)
            splitted = name.split('.')
            for sub in splitted[1:-1]:
                m = getattr(m, sub)
            return m
        except:
            log.error("Failed loading module: " + name + "\n" + traceback.format_exc())
            raise

    def registerPlugin(self, type_name, name, module, module_name, plugin):
        """
        Register plugin in the pluginsByName dict.
        
        Plugin will be installed if not already done.
        """

        if not self.isPluginInstalled(plugin._uuid):
            self.install(type_name, name, plugin._uuid)
        info = self.getPluginInfo(plugin._uuid)

        plugin._info = info
        self.pluginsByUuid[plugin._uuid.bytes] = plugin
        self.pluginsByName[name] = plugin
        self.pluginModules[plugin._uuid.bytes] = module
        self.pluginsByModule[module_name] = plugin

    def initPlugins(self):
        log.info('Initializing Plugins')
        for name, plugin in self.pluginsByName.iteritems():
            self.initPlugin(plugin)

        try:
            for name, plugin in self.pluginsByName.iteritems():
                plugin.checkDependencies()
        except:
            exc_class, val, tb = sys.exc_info()
            new_exc = Exception("Checking dependecies failed on: %s : %s" % (name, val or exc_class))
            raise new_exc.__class__, new_exc, tb

        events = [
                  'core.init',
                  'core.init.listeners',
                  'core.init.foreign'
                  ]
        for name in events:
            self.fireQuick(name + '.before')
            self.fireQuick(name)
            self.fireQuick(name + '.after')

    def fireQuick(self, name, *args, **kwargs):
        event = Event(None, name, *args, **kwargs)
        return self.fire(event)

    def fire(self, event):
        if env_.get('debug'):
            log.info('FIRING: ' + event._name)
        if self.pluginChainExists(event._name):
            self.pluginChains[event._name].fire(event)

        return event

    def pluginChainExists(self, name):
        return self.pluginChains.has_key(name)

    def listen(self, to, callback, config = None, position = -1):
        """
        Register a callback method and the parameters
        with which it is being executed with an event.
        """
        if not self.pluginChainExists(to):
            self.pluginChains[to] = PluginChain()

        self.pluginChains[to].add(callback, config)

    def initPlugin(self, plugin):
        """Initalize a plugin."""
        plugin.init()

    def getPluginInfo(self, uuid):
        #@todo: cache this info
        session = env_.get('db').createSession()
        info = session.query(_tables.PluginsTable).filter_by(uuid = uuid.bytes).one()
        info._release()
        return info

    def isPluginInstalled(self, uuid):
        """Return boolean whether a plugin is already installed."""
        try:
            self.getPluginInfo(uuid = uuid)
        except:
            return False
        return True

    def getListeners(self, name):
        """
        Returns a list of all the callbacks + configs that are
        listening to an event.
        This list is a copy of the original list, so
        changes are not being reflected.
        
        Return: callbacks[], configs[]
        """
        if self.pluginChainExists(name):
            callbacks = self.pluginChains[name].callbacks.copy()
            configs = self.pluginChains[name].configurations.copy()
            return callbacks, configs
        return {}, {}

    def install(self, type_name, name, uuid):
        """Install a plugin with the database."""
        type_id = self.getTypeId(type_name, True)
        session = env_.get('db').createSession()
        plugin = _tables.PluginsTable()
        plugin.name = unicode(name)
        plugin.uuid = uuid.bytes
        plugin.type_id = type_id
        plugin.version = 0
        session.add(plugin)
        session.flush()

    def getTypeId(self, type_name, create = False):
        type_name = unicode(type_name)
        session = env_.get('db').createSession()
        try:
            type = session.query(_tables.PluginTypesTable).filter_by(name = type_name).one()
        except:
            if not create:
                raise
            type = _tables.PluginTypesTable()
            type.name = type_name
            session.add(type)
            session.flush()
        return type.id

    def getPluginModule(self, a_uuid):
        try:
            return self.pluginModules[a_uuid]
        except:
            exc_class, val, tb = sys.exc_info()
            new_exc = Exception("No module found for UUID: %s : %s" % (uuid.UUID(a_uuid), val or exc_class))
            raise new_exc.__class__, new_exc, tb

    def getPluginByModule(self, module):
        """Get the instance of the plugin at that path"""
        return self.pluginsByModule[module]

    def getMyPlugin(self, module, subcount = 0):
        splitted = module.split(".")
        shortened = ".".join(splitted[:-(subcount + 1)])
        return self.getPluginByModule(shortened)

