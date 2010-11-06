from app.lib import event
from app.core import util
class Widget(object):
    def __init__(self, name, owner):
        self._withErrorHandler = lambda a, b, c: False

    def __start__(self):
        return WidgetContext(self, self._withErrorHandler)

    def __exit__(self, type, value, traceback):
        return self.error_handler(type, value, traceback)

    def blacklist(self, list):
        def _blacklist(type, value, traceback):
            return type.__class__ in list
        self._withErrorHandler = _blacklist
        return self

    def whitelist(self, list):
        def _whitelist(self, list):
            return type.__class__ in list
        self._withErrorHandler = _whitelist
        return self

class NewWidgetDescriptor(object):
    """
    Descriptor for the WidgetManager's newWidget attribute
    to register new widgets by assigning to it.
    """
    def __init__(self):
        self._defaults = (None, None, [], {})
    def __get__(self, instance, owner):
        raise AttributeError("Must not read from WidgetExporter")
    def __set__(self, obj, val):
        defaults = list(self._defaults)
        (name, obj_type, args, kwargs) = util.list_apply_defaults(val, defaults)
        obj.importWidget(name, obj_type, *args, **kwargs)

class WidgetManager(object):
    newWidget = NewWidgetDescriptor()
    """
    Registers calls registerWidget when being written to.
    Read access disabled. Throws exception
    """

    def __init__(self, owner):
        self._owner = owner
        self._classes = {}

    @event.extract
    def _registerWidget(self, name, callback, config, _event = None, _config = None):
        """
        Listening to: frontent.widget.new
        """
        uuid = _event._sender._uuid
        self.registerWidget(name, uuid, callback, config)

    def registerWidget(self, name, uuid, callback, config):
        lib = self._widgetClasses
        by_plugin = lib[uuid] = lib[uuid] if uuid in lib else  {}
        if not name in by_plugin:
            by_plugin[name] = {
                'callback' : callback
                , 'config': config
            }

    def getWidgetExporter(self, event, config):
        event.addResult(self)

    def importWidget(self, *args, **kwargs):
        #@todo: Implement Widget adding
        pass

class WidgetContext(object):
    def __init__(self, owner, areas):
        self._registeredWidgets = {}

    def _registerWidget(self, name, callback, *args, **kwargs):
        """Register a subwidget with the current widget context."""
        if not name in self._registeredWidgets:
            self._registeredWidgets[name] = (callback, args, kwargs)
        else:
            raise RuntimeError("Widget already exists: %s" % name)

    def render(self, template, variables):
        pass

class WidgetContainer(object):
    def __init__(self):
        pass

    def create(self, name, *args, **kwargs):
        pass

    def __get__(self, obj, type = None):
        return value

    def __set__(self, obj, value):
        return None

class Util(object):
    pass
