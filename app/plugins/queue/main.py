from app.lib.bones import PluginBones
from . import _tables
import uuid

class Queue(PluginBones):
    """This plugin provides the download queue"""

    def _identify(self):
        return uuid.UUID('f3400618-b4a4-4371-a672-e58d4bd4afb7')

    def init(self):
        self._upgradeDatabase(_tables.latestVersion, _tables)

    def postConstruct(self):
        pass
        #_tables.bootstrap(env_.get('db'))

    def _getDependencies(self):
        #@todo: implement dependencies
        return {}
