from app.lib import event
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

class WidgetManager(object):
    def __init__(self, owner):
        self._owner = owner
        self._widgetClasses = {}

    @event.extract
    def registerWidget(self, name, callback, config, _event = None, _config = None):
        """
        Listening to: frontent.widget.export
        """
        uuid = _event._sender._uuid

        lib = self._widgetClasses
        by_plugin = lib[uuid] = lib[uuid] if uuid in lib else  {}
        if not name in by_plugin:
            by_plugin[name] = {
                'callback' : callback
                , 'config': config
            }

class WidgetContext(object):
    def __init__(self, owner):
        pass
