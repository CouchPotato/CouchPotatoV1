from app.core import env_
from app.core.frontend import Route
from app.core.environment import Environment as env_
from app.lib.bones import PluginBones
from app.plugins.movies import _tables
from app.plugins.movies.controller import MovieController

class Movies(PluginBones):
    '''
    This plugin provides the movie library for CouchPotato
    '''

    def init(self):
        self._upgradeDatabase(_tables.latestVersion, _tables)
        controller = self._createController((), MovieController)
        route = Route(controller = controller, route = '/movie/')
        self._fire('frontend.route.register', route)

    def postConstruct(self):
        _tables.bootstrap(env_.get('db'))

