from app.lib.bones import PluginBones
import uuid

class Couchpotato(PluginBones):
    '''
    This class initializes all the plugins and links
    them toghether for a default CP setup.
    
    This should be replaced once the plugin system
    is fully functional with a GUI to create
    custom plugin toolchains.
    '''

    def postConstruct(self):
        pass

    def _identify(self):
        return uuid.UUID('911ab777-2840-47c5-8692-ed120b6a5c65')
