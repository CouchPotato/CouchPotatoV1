from .environment import Environment as env_
import os, glob
from app.core import getLogger
log = getLogger(__name__)

class PluginLoader:
    def __init__(self):
        self.plugins = {}
        self.paths = (
                      os.path.join(env_.get('appDir'), 'app', 'lib', 'plugins'),
                      os.path.join(env_.get('dataDir'), 'plugins')
                      )
        for dir in self.paths:
            self.loadFromDir(dir)

        if self.plugins.__len__():
            log.info('Plugins loaded: ' + str(self.plugins.__len__()))
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
            self.plugins[name] = getattr(m, name).start()
        except:
            log.error('Failed loading plugin: ' + name)

