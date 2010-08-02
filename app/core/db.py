import sqlalchemy as sql_
import sqlalchemy.orm as sql_orm_
import sqlalchemy.types as sql_t_
from app.core import getLogger
import os


log = getLogger(__name__)
class Database(object):
    typeLookup = {
         'i' :   sql_t_.Integer,
         's' :   sql_t_.String,
         'b' :   sql_t_.Boolean,
         't' :   sql_t_.Text,
         'us' :   sql_t_.Unicode,
         'ut' :   sql_t_.UnicodeText
    }
    '''
    Provides a database abstraction
    '''
    def __init__(self, file):
        '''
        Constructor
        '''
        self.engine = sql_.create_engine('sqlite:///%s' % file)
        self.metadata = sql_.schema.MetaData(self.engine)

    def createSession(self):
        return sql_orm_.scoped_session(
                sql_orm_.sessionmaker(bind = self.engine, autocommit = True)
        ) #END return session

    def getTable(self, name, columns):
        columns = [self.getColumn(column) for column in columns]
        return sql_.schema.Table(
            name,
            self.metadata,
            *columns
        )

    def getAutoIdTable(self, name, columns):
        columns.insert(0, self.getColumn('id', 'i', primary_key = True))
        return self.getTable(
            self
        )

    def getColumn(self, name, type, **args):
        if Database.typeLookup.has_key(type):
            type = Database.typeLookup[type]

        return sql_.schema.Column(
            name,
            type,
            **args
        )

