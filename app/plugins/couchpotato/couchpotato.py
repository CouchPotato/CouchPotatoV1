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
        self._listen('core.init.foreign', self.initForeign)

    def initForeign(self, event, config):
        event = self._fire('frontend.widgets.requestExporter')
        exporter = event.getResultSet()[0]
        exporter.newWidget = ['test', 'testing']

    def _identify(self):
        return uuid.UUID('911ab777-2840-47c5-8692-ed120b6a5c65')

    def _getDependencies(self):
        return {
            'core' : '34e50abc-bbdd-477c-b1e2-bb28c7fcdb7d',
            'frontend' : '87aece57-2948-4cab-aad1-8b2190e71873',
            'minify' : '87aece57-2948-4cab-aad1-8b2190e71873',
        }
