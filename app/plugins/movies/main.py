from app.core import env_
from app.core.frontend import Route
from app.core.environment import Environment as env_
from app.lib.bones import PluginBones
from app.plugins.movies import _tables
from app.plugins.movies.controller import MovieController
import uuid

class Movies(PluginBones):
    def _identify(self):
        return uuid.UUID('52e07796-fdec-445a-89ef-d3515ca04da2')
    def init(self):
        # Create database
        self._upgradeDatabase(_tables.latestVersion, _tables)

        # Add controller to route
        controller = self._createController((), MovieController)
        route = Route(controller = controller, route = '/movie/')
        self._fire('frontend.route.register', route)

    def postConstruct(self):
        _tables.bootstrap(env_.get('db'))

