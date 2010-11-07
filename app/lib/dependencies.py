import uuid
from app.core import env_, util
from app.core import getLogger

log = getLogger(__name__)
class Dependencies(object):
    def __init__(self, dependencies):
        self._dependencies = {}
        self._lookup = {}
        self.addDependencies(dependencies)

    def addDependencies(self, dependencies):
        for alias, a_uuid in dependencies.iteritems():
            self.addDependency(alias, a_uuid)

    def addDependency(self, alias, a_uuid):
        a_uuid = a_uuid if isinstance(a_uuid, uuid.UUID) else uuid.UUID(a_uuid)
        if not alias in self._dependencies:
            self._dependencies[alias] = a_uuid
        self.resolve(alias)

    def resolve(self, alias):
        if alias in self._lookup:
            return self._lookup[alias]

        if alias not in self._dependencies.keys():
            raise RuntimeError("Unknown alias: %s" % alias)

        uuid = self._dependencies[alias]

        try:
            plugin = env_._pluginMgr.pluginsByUuid[uuid.bytes] #@UndefinedVariable
        except KeyError:
            if not env_._pluginMgr.isPluginInstalled(uuid): #@UndefinedVariable
                log.error("Requested plugin is not installed: %s:%s" % (alias, str(uuid)))
            else:
                log.error("Unable to resolve alias, plugin not loaded: %s:%s" % (alias, str(uuid)))
            raise
        self._lookup[alias] = plugin

    def asObject(self):
        plugins = {name : self.resolve(name) for name in self._dependencies}
        return util.ValueObject(plugins)
