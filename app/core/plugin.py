from .environment import Environment as env_
from app.core import getLogger
from app.core.db import _tables
from app.lib.chain import Chain as PluginChain
from app.lib.event import Event
import os
import glob
import sys
import traceback
log = getLogger(__name__)

class PluginLoader:
    def __init__(self):
        env_._pluginMgr = self
        self.pluginChains = {}
        self.plugins = {}
        self.paths = {
                      'core' : ('app.plugins.', os.path.join(env_.get('appDir'), 'app', 'plugins')),
                      'user' : ('plugins.', os.path.join(env_.get('dataDir'), 'plugins'))
                      }
        for type, tuple in self.paths.iteritems():
            self.loadFromDir(type, tuple[0], tuple[1])

        if len(self.plugins):
            log.info('Plugins loaded: ' + str(len(self.plugins)))
            self.initPlugins()
        else:
            log.info('No plugins have been loaded.')

    def loadFromDir(self, type, module, dir):
        """Load each directory as plugin."""
        for file in glob.glob(os.path.join(dir, '*')):
            plugin_name = os.path.basename(file)
            plugin_dir = os.path.join(dir, plugin_name)
            if os.path.isdir(plugin_dir):
                self.loadPlugin(type, module, plugin_name, plugin_dir)

    def loadPlugin(self, type, module, name, path):
        """Load individual directory as plugin."""
        log.info('Loading plugin: ' + module + name)
        try:
            m = self.loadModule(module + name)
            self.registerPlugin(type, name, getattr(m, name).start(name, self, path))
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

    def registerPlugin(self, type_name, name, plugin):
        """
        Register plugin in the plugins dict.
        
        Plugin will be installed if not already done.
        """

        if not self.isPluginInstalled(plugin._uuid):
            self.install(type_name, name, plugin._uuid)
        info = self.getPluginInfo(plugin._uuid)

        plugin._info = info
        self.plugins[name] = plugin

    def initPlugins(self):
        log.info('Initializing Plugins')
        for name, plugin in self.plugins.iteritems():
            self.initPlugin(plugin)

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
