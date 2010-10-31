from app.core import env_
from app.core.frontend import Route
from app.lib.bones import PluginBones
from app.plugins.movies import _tables
from app.plugins.movies.controller import MovieController

class Movies(PluginBones):
    '''
    This plugin provides the movie library
    '''

    def init(self):
        # Create database
        self._upgradeDatabase(_tables.latestVersion, _tables)

        # Add controller to route
        controller = self._createController((), MovieController)
        route = Route(controller = controller, route = '/movie/:action/', action = 'index')
        self._fire('frontend.route.register', route)
        
        self.registerHead()

    def postConstruct(self):
        _tables.bootstrap(env_.get('db'))
        
    def registerHead(self):
        
        self._fire('registerScript', file = 'script/movie.js')
        self._fire('registerStyle', file = 'style/search.css')

