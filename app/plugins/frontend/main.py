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
        self._widgetMgr = widgets.WidgetManager(self)
        self.frontend = env_.get('frontend')
        self._listen('core.init.listeners', self.initListeners)
        self._export(widget = widgets.Widget)
        self.installWidgetMethods()

    def initListeners(self, core, config):
        self._listen('frontend.route.register', self.registerRoute)
        self._listen('frontend.widgets.requestExporter', self._widgetMgr.getWidgetExporter)
        self._listen('frontend.widgets.new', self._widgetMgr._registerWidget)

    def registerRoute(self, event, config):
        route = event._args[0]
        self.frontend.addRoute(route)

    def _getDependencies(self):
        #@todo: implement dependencies
        return {}

    def installWidgetMethods(self):
        """
        Add new methods to the PluginBones object
        to enable widget functionality on all
        objects both existent and to be created.
        """
        widget_mgr = self._widgetMgr
        def myenter(myself):
            myself._widgets.create(plugin = myself)
            return widgets.WidgetContext(myself)

        def myexit(myself, type, value, traceback):
            pass

        class WidgetManagerWrapper(object):
            def __init__(self):
                self._owner = None

            def __getattr__(self, name):
                method = getattr(widget_mgr, name)
                def wrapper(*args, **kwargs):
                    return method(self._owner, *args, **kwargs)
                return wrapper

            def __get__(self, owner, type):
                self._owner = owner
                return self

            def __enter__(self):
                pass

            def __exit__(self, type, value, traceback):
                pass

        PluginBones.__enter__ = myenter
        PluginBones.__exit__ = myexit
        PluginBones._widgets = WidgetManagerWrapper()

