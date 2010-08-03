from app.lib.plugin.bones import PluginBones, PluginController
from app.lib.plugin.event import Event
import cherrypy
from app.core.frontend import Route

class SomeController(PluginController):
    @cherrypy.expose
    def index(self):
        return self.render('index.html')


class CouchCore(PluginBones):
    '''
    classdocs
    '''

    def postConstruct(self):
        pass

    def init(self):
        controller = self.createController((), SomeController)
        route = Route(controller = controller, route = '/')
        self._fire('frontend.route.register', route)
