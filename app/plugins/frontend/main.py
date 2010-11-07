from app.lib.bones import PluginBones
from app.core import getLogger
from app.core import env_
from . import widgets
import uuid

log = getLogger(__name__)

class Frontend(PluginBones):
    '''
    Provides an interterface for plugins to register with the frontend
    '''

    def _identify(self):
        return uuid.UUID('87aece57-2948-4cab-aad1-8b2190e71873')


    def postConstruct(self):
        self.tabs = {}
        self._widgets = widgets.WidgetManager(self)
        self.frontend = env_.get('frontend')
        self._listen('core.init.listeners', self.initListeners)
        self._export(widget = widgets.Widget)

    def initListeners(self, core, config):
        self._listen('frontend.route.register', self.registerRoute)
        self._listen('frontend.widgets.requestExporter', self._widgets.getWidgetExporter)
        self._listen('frontend.widgets.new', self._widgets._registerWidget)

    def registerRoute(self, event, config):
        route = event._args[0]
        self.frontend.addRoute(route)

    def _getDependencies(self):
        #@todo: implement dependencies
        return {}

