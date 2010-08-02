from .environment import Environment as env_
import os, glob
from app.core import getLogger
import sys, traceback
from app.lib.plugin.chain import Chain as PluginChain
log = getLogger(__name__)

class PluginLoader:
    def __init__(self):
        env_._pluginMgr = self
        self.plugins = {}
        self.pluginChains = {}
        self.paths = (
                      os.path.join(env_.get('appDir'), 'app', 'lib', 'plugins'),
                      os.path.join(env_.get('dataDir'), 'plugins')
                      )
        for dir in self.paths:
            self.loadFromDir(dir)

        if self.plugins.__len__():
            log.info('Plugins loaded: ' + str(self.plugins.__len__()))
            self.initPlugins()
        else:
            log.info('No plugins have been loaded.')

    def loadFromDir(self, dir):
        for file in glob.glob(os.path.join(dir, '*')):
            plugin_name = os.path.basename(file)
            plugin_dir = os.path.join(dir, plugin_name)
            if os.path.isdir(plugin_dir):
                self.loadPlugin(plugin_name, plugin_dir)

    def loadPlugin(self, name, path):
        log.info('Loading plugin: ' + name)
        try:
            m = __import__('plugins.' + name)
            self.registerPlugin(name, getattr(m, name).start(name, self))
        except:
            log.error("Failed loading plugin: " + name + "\n" + traceback.format_exc())

    def registerPlugin(self, name, plugin):
        self.plugins[name] = plugin

    def initPlugins(self):
        log.info('Initializing Plugins')
        for name, plugin in self.plugins.iteritems():
            self.initPlugin(plugin)

    def fire(self, name, event):
        if self.pluginChainExists(name):
            self.pluginChains[name].fire(event)


    def pluginChainExists(self, name):
        return self.pluginChains.has_key(name)

    def listen(self, to, callback, config, position = -1):
        if not self.pluginChainExists(to):
            self.pluginChains[to] = PluginChain()

        self.pluginChains[to].add(callback, config)

    def initPlugin(self, plugin):
        plugin.init()


