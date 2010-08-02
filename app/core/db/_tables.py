import db
from sqlalchemy.orm import mapper
from sqlalchemy.schema import UniqueConstraint

class BasicTable(object):
    def __repr__(self):
        return "<" + self.__class__.__name__ + ": "

class VersionsTable(BasicTable):
    id = None
    key = None
    type = None
    version = None
    def __repr__(self):
        return BasicTable.__repr__(self) + self.key + "=" + self.value

class ModuleTypesTable(BasicTable):
    id = None
    module = None
    type = None
    version = None
    pass


def bootstrap(db):
    columns = [
        [['module', 's'], {}],
        [['type', 'i'], {}],
        [['version', 'i'], {}]
    ]
    unique = UniqueConstraint('module', 'type', name = 'moduleType')
    versionsTable = db.getAutoIdTable('versions', columns, unique)

    moduleTypesTable = db.getAutoIdTable('module_types', [[['type', 's'], {}]])
    mapper(VersionsTable, versionsTable)
    mapper(ModuleTypesTable, moduleTypesTable)
