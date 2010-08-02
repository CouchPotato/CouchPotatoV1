import sqlalchemy as sql_
import sqlalchemy.orm as sql_orm_
import sqlalchemy.types as sql_t_
from app.core import getLogger
import _tables
import os


log = getLogger(__name__)
class Database(object):
    typeLookup = {
         'i' :   sql_t_.Integer,
         's' :   sql_t_.Unicode,
         'b' :   sql_t_.Boolean,
         't' :   sql_t_.UnicodeText
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

        log.info('Loading Database...')
        _tables.bootstrap(self)
        """
        doUpgrade = os.path.isfile(path):

        metadata.create_all()

        if doUpgrade:
            #upgradeDb()
            pass
        else:
            for nr in range(1, latestDatabaseVersion + 1):
                Session.add(DbVersion(nr))
                Session.flush()
        log.info('Database loaded')
        """

    def createSession(self):
        return sql_orm_.scoped_session(
                sql_orm_.sessionmaker(bind = self.engine, autocommit = True)
        ) #END return session

    def getTable(self, name, columns):
        columns = [self.getColumn(name_, type_, **kwargs_) for name_, type_, kwargs_ in columns]
        return sql_.schema.Table(
            name,
            self.metadata,
            *columns
        )

    def getAutoIdTable(self, name, columns):
        columns.insert(0, ('id', 'i', {'primary_key' : True}))
        return self.getTable(
            name, columns
        )

    def getColumn(self, name, type, **kwargs):
        if Database.typeLookup.has_key(type):
            type = Database.typeLookup[type]

        return sql_.schema.Column(
            name,
            type,
            **kwargs
        )

