from app.core.environment import Environment as env_
from app.lib.bones import PluginBones, PluginController
import uuid
from . import widgets
from app.core.frontend import Route
import cherrypy


class CoreController(PluginController):
    @cherrypy.expose
    def index(self):
        vars = {'baseUrl' : env_.get('baseUrl')}
        with self.plugin._widgets('base') as base:
            with base['menu'] as menu:
                with menu.creating('tab') as tabs:
                    tabs.create(1)
                    tabs.create(2)

            pass

        return self.render('base.html', vars)

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
        widgets.load(self)

        controller = self._createController((), CoreController)
        route = Route(controller = controller, route = '/')
        self._fire('threaded.event.wait', 'frontend.route.register', route)

    def _identify(self):
        return uuid.UUID('911ab777-2840-47c5-8692-ed120b6a5c65')

    def _getDependencies(self):
        return {
            'core' : '34e50abc-bbdd-477c-b1e2-bb28c7fcdb7d',
            'frontend' : '87aece57-2948-4cab-aad1-8b2190e71873',
            'minify' : '87aece57-2948-4cab-aad1-8b2190e71873',
        }
