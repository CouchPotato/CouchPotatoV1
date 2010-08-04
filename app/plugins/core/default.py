from app.lib.bones import PluginBones, PluginController
from app.lib.event import Event
import cherrypy
from app.core.frontend import Route
from app.core.environment import Environment as env_

class CoreController(PluginController):
    @cherrypy.expose
    def index(self):
        vars = {'baseUrl' : env_.get('baseUrl')}
        return self.render('index.html', vars)


class CouchCore(PluginBones):
    '''
    classdocs
    '''

    def postConstruct(self):
        pass

    def init(self):
        controller = self._createController((), CoreController)
        route = Route(controller = controller, route = '/')
        self._fire('frontend.route.register', route)

    def spawnThreadedEvent(self, event, config):
        self._pluginMgr.get
