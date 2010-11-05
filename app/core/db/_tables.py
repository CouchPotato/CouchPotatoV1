from sqlalchemy.orm import mapper
from sqlalchemy.schema import UniqueConstraint
from app.core.environment import Environment as env_

latestVersion = 1

class BasicTable(object):
    def __repr__(self):
        return "<" + self.__class__.__name__ + ": "
    def _release(self):
        env_.get('db').session.object_session(self).expunge(self)

class PluginsTable(BasicTable):
    def __init__(self, name = None, type_id = None, uuid = None, version = None):
        self.name = unicode(name)
        self.type_id = type_id
        self.uuid = uuid
        self.version = version

    def __repr__(self):
        return BasicTable.__repr__(self) + self.name + str(self.version)

class PluginTypesTable(BasicTable):
    def __init__(self, name = None):
        self.name = unicode(name)


def bootstrap(db):
    columns = [
        [['name', 's'], {}],
        [['type_id', 'i'], {}],
        [['uuid', ['x', [16] ] ], {}],
        [['version', 'i'], {}],
    ]
    unique = UniqueConstraint('name', 'type_id', name = 'pluginType')
    pluginsTable = db.getAutoIdTable('plugins', columns, unique)

    moduleTypesTable = db.getAutoIdTable('plugin_types', [[['name', 's'], {}]])
    mapper(PluginsTable, pluginsTable)
    mapper(PluginTypesTable, moduleTypesTable)

    db.create()


def migrateToVersion2():
    pass
