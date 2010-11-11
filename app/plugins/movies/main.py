from app.core import env_
from app.core.frontend import Route
from app.lib.bones import PluginBones
from . import _tables
from .controller import MovieController
import uuid

class Movies(PluginBones):
    '''
    This plugin provides the movie library for CouchPotato
    '''

    def _identify(self):
        return uuid.UUID('52e07796-fdec-445a-89ef-d3515ca04da2')
    def init(self):
        # Create database
        self._upgradeDatabase(_tables.latestVersion, _tables)

        # Add controller to route
        controller = self._createController(MovieController)
        route = Route(controller = controller, route = '/movie/:action', action = 'index')
        self._fire('frontend.route.register', route)

        self.registerHead()

    def postConstruct(self):
        _tables.bootstrap(env_.get('db'))

    def registerHead(self):
        self._fire('registerScript', file = 'movie.js')
        self._fire('registerStyle', file = 'search.css')

    def _getDependencies(self):
        #@todo: implement dependencies
        return {}
