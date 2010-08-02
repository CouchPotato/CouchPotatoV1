import db
from sqlalchemy.orm import mapper
from sqlalchemy.schema import UniqueConstraint
from app.core.environment import Environment as env_

class BasicTable(object):
    def __repr__(self):
        return "<" + self.__class__.__name__ + ": "
    def _release(self):
        env_.get('db').session.object_session(self).expunge(self)

class PluginsTable(BasicTable):
    id = None
    name = None
    type = None
    version = None
    def __repr__(self):
        return BasicTable.__repr__(self) + self.name + str(self.version)

class PluginTypesTable(BasicTable):
    id = None
    module = None
    type = None
    version = None


def bootstrap(db):
    columns = [
        [['name', 's'], {}],
        [['type_id', 'i'], {}],
        [['version', 'i'], {}]
    ]
    unique = UniqueConstraint('name', 'type_id', name = 'pluginType')
    pluginsTable = db.getAutoIdTable('plugins', columns, unique)

    moduleTypesTable = db.getAutoIdTable('plugin_types', [[['name', 's'], {}]])
    mapper(PluginsTable, pluginsTable)
    mapper(PluginTypesTable, moduleTypesTable)

    db.create()
