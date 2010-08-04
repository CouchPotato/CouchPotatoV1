from .environment import Environment as env_
import os, glob
from app.core import getLogger
import sys, traceback
from app.lib.chain import Chain as PluginChain
from app.core.db import _tables
from app.lib.event import Event
log = getLogger(__name__)

class PluginLoader:
    def __init__(self):
        env_._pluginMgr = self
        env_._coreInfo = self.getCoreInfo()
        self.plugins = {}
        self.pluginChains = {}
        self.paths = {
                      'core' : ('app.plugins.', os.path.join(env_.get('appDir'), 'app', 'plugins')),
                      'user' : ('plugins.', os.path.join(env_.get('dataDir'), 'plugins'))
                      }
        for type, tuple in self.paths.iteritems():
            self.loadFromDir(type, tuple[0], tuple[1])

        if self.plugins.__len__():
            log.info('Plugins loaded: ' + str(self.plugins.__len__()))
            self.initPlugins()
        else:
            log.info('No plugins have been loaded.')

    def loadFromDir(self, type, module, dir):
        for file in glob.glob(os.path.join(dir, '*')):
            plugin_name = os.path.basename(file)
            plugin_dir = os.path.join(dir, plugin_name)
            if os.path.isdir(plugin_dir):
                self.loadPlugin(type, module, plugin_name, plugin_dir)

    def loadPlugin(self, type, module, name, path):
        log.info('Loading plugin: ' + module + name)
        try:
            m = self.loadModule(module + name)
            self.registerPlugin(type, name, getattr(m, name).start(name, self, path))
        except:
            log.error("Failed loading plugin: " + name + "\n" + traceback.format_exc())

    def loadModule(self, name):
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
        if not self.isPluginInstalled(name, type_name):
            self.install(type_name, name)
        info = self.getPluginInfo(name, type_name)

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
            self.fireQuick(name + '.pre')
            self.fireQuick(name)
            self.fireQuick(name + '.post')

    def fireQuick(self, name, input = None):
        event = Event(None, name, input)
        self.fire(event)

    def fire(self, event):
        if env_.get('debug'):
            log.info('FIRING: ' + event._name)
        if self.pluginChainExists(event._name):
            self.pluginChains[event._name].fire(event)

    def pluginChainExists(self, name):
        return self.pluginChains.has_key(name)

    def listen(self, to, callback, config = None, position = -1):
        if not self.pluginChainExists(to):
            self.pluginChains[to] = PluginChain()

        self.pluginChains[to].add(callback, config)

    def initPlugin(self, plugin):
        plugin.init()

    def getPluginInfo(self, name, type_name):
        session = env_.get('db').createSession()
        name = unicode(name)
        type_id = self.getTypeId(type_name, False)
        info = session.query(_tables.PluginsTable).filter_by(type_id = type_id, name = name).one()
        info._release()
        return info

    def isPluginInstalled(self, name, type_name = 'user'):
        try:
            self.getPluginInfo(name, type_name)
        except:
            return False
        return True

    def install(self, type_name, name):
        type_id = self.getTypeId(type_name, True)
        name = unicode(name)
        session = env_.get('db').createSession()
        plugin = _tables.PluginsTable()
        plugin.name = name
        plugin.type_id = type_id
        plugin.version = 0
        session.add(plugin)
        session.flush()

    def getCoreInfo(self):
        if not self.isPluginInstalled('core', 'core'):
            raise ValueError('No core version found')
        info = self.getPluginInfo('core', 'core')
        return info


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



