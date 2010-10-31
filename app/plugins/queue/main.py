from app.core import env_
from app.lib.bones import PluginBones
from app.plugins.queue import _tables

class Queue(PluginBones):
    '''
    This plugin provides the download queue
    '''

    def init(self):
        self._upgradeDatabase(_tables.latestVersion, _tables)

    def postConstruct(self):
        pass
        #_tables.bootstrap(env_.get('db'))
