from app.lib import event
from app.core import util, env_, getLogger
from collections import defaultdict #@UnresolvedImport - why?

log = getLogger(__name__)

def load():
    owner = env_._pluginMgr.getMyPlugin(__name__) #@UndefinedVariable
    class Widget(object):
        def __init__(self, name, plugin, *args, **kwargs):
            owner._widgetMgr.registerWidget(name, plugin._identify(), self._execute, args, kwargs)
            pass

        def _execute(self, args, kwargs, config_args, config_kwargs):
            pass

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
            self._widgets = defaultdict(dict)

        @event.extract
        def _registerWidget(self, name, callback, config, _event = None, _config = None):
            """
            Listening to: frontent.widget.new
            """
            uuid = _event._sender._uuid
            self.registerWidget(name, uuid, callback, config)

        def registerWidget(self, name, uuid, callback, *args, **kwargs):
            lib = self._widgets
            by_plugin = lib[uuid.bytes]
            if not name in by_plugin:
                by_plugin[name] = WidgetConfiguration(callback, args, kwargs)

        def getWidgetExporter(self, event, config):
            event.addResult(self)

        def importWidget(self, *args, **kwargs):
            #@todo: Implement Widget adding
            pass

        def printPlugin(self, plugin, *args, **kwargs):
            print plugin, args

        def __enter__(self, plugin):
            """Create a new WidgetContext for a plugin"""
            return WidgetContext(None, plugin)

        def __exit__(self, *args):
            print args

        def __call__(self, plugin, name, *args, **kwargs):
            uuid = plugin._identify()
            if uuid.bytes in self._widgets:
                if name in self._widgets[uuid.bytes]:
                    config = self._widgets[uuid.bytes][name]
                    return WidgetContext(None, plugin, args, kwargs, config)
                raise AttributeError("No widgets registered for this name.")
            raise AttributeError("No widgets registered for this uuid: %s" % uuid)

    class WidgetConfiguration(object):
        def __init__(self, callback, args, kwargs):
            self._callback = callback
            self._args = args
            self._kwargs = kwargs

        def __call__(self, context, *args, **kwargs):
            return self._callback(context, args, kwargs, self._args, self._kwargs)

    class WidgetContext(object):
        def __init__(self, parent_context, plugin, args, kwargs, widget_config = None):
            self._parentContext = parent_context
            self._widgetMgr = owner._widgetMgr
            self._widgetConfig = widget_config
            self._plugin = plugin
            self._args = args
            self._kwargs = kwargs
            self._containers = defaultdict(self._createContainer)

        def _createContainer(self, plugin_ = None):
            return WidgetContainer(self)

        def __getitem__(self, name):
            """Access a named subcontext."""
            return self._containers[name]

        def __enter__(self, *args):
            return self

        def __exit__(self, *args):
            pass

        def __call__(self):
            return self._widgetConfig(self, *self._args, **self._kwargs)

    class CreatingHelper(object):
        def __init__(self, owning_container, plugin, name):
            self._owningContainer = owning_container
            self._plugin = plugin
            self._name = name

        def create(self, *args, **kwargs):
            self._owningContainer.create(self._name, *args, **kwargs)

        def __enter__(self, *args):
            return self

        def __exit__(self, *args):
            pass

    class WidgetContainer(object):
        def __init__(self, context):
            self._context = context
            self._widgets = []
            self._str = None

        def creating(self, name, plugin = None):
            """Create multiple WidgetContexts of the same type."""
            plugin = plugin or self._context._plugin
            return CreatingHelper(self, plugin, name)

        def create(self, name, *args, **kwargs):
            """Create new WidgetContext."""
            return self.createAt(name, None, *args, **kwargs)

        def createAt(self, name, position = None, *args, **kwargs):
            position = position or len(self._widgets)
            context = owner._widgetMgr(
                self._context._plugin,
                name,
                *args,
                __owner = self, **kwargs
            )
            self._widgets.insert(position, context)
            return context

        def __enter__(self, *args):
            return self

        def __exit__(self, *args):
            self()
            pass

        def __call__(self):
            return "".join([x() for x in self._widgets])

        def __str__(self):
            if not self._str:
                self._str = self()
            return self._str

    owner._widgetMgr = WidgetManager(owner)
    owner.frontend = env_.get('frontend')
    owner._listen('core.init.listeners', owner.initListeners)
    owner._export(widget = Widget)
    owner.installWidgetMethods()
