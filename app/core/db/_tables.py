import db
from sqlalchemy.orm import mapper

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
    columns = (
        ('module', 's', {'unique' : 'versions'}),
        ('type', 'i', {'unique' : 'versions'}),
        ('version', 'i', {})
    )
    versionsTable = db.getAutoIdTable('versions', columns)

    moduleTypesTable = db.getAutoIdTable('module_types', [('type', 's', {})])
    mapper(VersionsTable, versionsTable)
    mapper(moduleTypesTable)






