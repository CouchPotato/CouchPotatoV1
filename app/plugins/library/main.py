from app.lib.bones import PluginBones
import uuid
class Library(PluginBones):
    """This plugin provides the movie library for CouchPotato"""
    def _identify(self):
        return uuid.UUID('0becb208-3ec4-4301-b57a-e114c574d989')
    def postConstruct(self):
        pass

    def _getDependencies(self):
        return {}
