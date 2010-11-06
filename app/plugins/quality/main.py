from app.core import env_
from app.lib.bones import PluginBones
from app.plugins.quality import _tables
import uuid

class Quality(PluginBones):
    """This plugin provides the movie library for CouchPotato"""

    def _identify(self):
        return uuid.UUID('3596fd6d-4a28-49db-8dcf-4ff7c10db294')

    def init(self):
        self._upgradeDatabase(_tables.latestVersion, _tables)

    def postConstruct(self):
        pass
        #_tables.bootstrap(env_.get('db'))
