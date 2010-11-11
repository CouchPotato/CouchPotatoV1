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

    def init(self):
        widgets.load()

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
        class WidgetManagerWrapper(object):
            """
            Allow plugins to access WidgetManager
            functionality without having to pass
            the instance manually.
            
            Uses Descriptor protocol to get the instance
            automatically and __getattr__ to dynamically
            create a wrapper and passing the previously
            fetched instance along as first argument.
            """
            def __init__(self):
                """Ensure existance of _owner"""
                self._owner = None

            def __getattr__(self, name):
                """Wrap/decorate Wmgr method on the fly."""
                if hasattr(widget_mgr, name):
                    method = getattr(widget_mgr, name)
                    def wrapper(*args, **kwargs):
                        return method(self._owner, *args, **kwargs)
                    return wrapper
                else:
                    AttributeError("WidgetManager has no attribute %s" % name)

            def __get__(self, owner, type):
                """Automatically get instance of the current plugin."""
                self._owner = owner
                return self

            def __enter__(self):
                """
                Defining our own magic methods.
                When automagically invoked, they are being looked up
                in on the class object, not the instance's __dict__
                Ergo __getattr__ is never called
                
                See: http://docs.python.org/reference/datamodel#special-method-names
                    For instance, if a class defines a method named __getitem__(),
                    and x is an instance of this class, then x[i] is roughly
                    equivalent to x.__getitem__(i) for old-style classes and
                    type(x).__getitem__(x, i) for new-style classes.
                        November, 10th, 2010
                Also: http://bugs.python.org/issue9259
                    Magic methods are looked up on the object's class,
                    not in the object's __dict__.
                        November, 10th, 2010
                """
                return widget_mgr.__enter__(self._owner)

            def __exit__(self, *args):
                """See comment from `__enter__`"""
                return widget_mgr.__exit__(*args)

            def __call__(self, *args, **kwargs):
                """Create WidgetContext with Widget"""
                return widget_mgr(self._owner, *args, **kwargs)

        PluginBones._widgets = WidgetManagerWrapper()

