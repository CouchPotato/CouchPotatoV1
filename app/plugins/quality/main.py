from app.core import env_
from app.lib.bones import PluginBones
from app.plugins.quality import _tables

class Quality(PluginBones):
    '''
    This plugin provides the movie library for CouchPotato
    '''

    def init(self):
        self._upgradeDatabase(_tables.latestVersion, _tables)

    def postConstruct(self):
        pass
        #_tables.bootstrap(env_.get('db'))
