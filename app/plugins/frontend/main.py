from app.core import getLogger, env_
from app.lib.bones import PluginBones

log = getLogger(__name__)

class Frontend(PluginBones):
    '''
    Provides an interface for plugins to register with the frontend
    '''

    def postConstruct(self):
        self.tabs = {}
        self._listen('frontend.route.register', self.registerRoute)
        self.frontend = env_.get('frontend')

    def registerRoute(self, event, config):
        route = event._args[0]
        self.frontend.addRoute(route)


    def export(self):
        return {
            'frontend' : (
                          'discoverTabs'
                          )
                }

    def addTab(self, name, title, controller):
        pass

    def addSmallTab(self, name, title, controller):
        pass


