import sqlalchemy as sql_
import sqlalchemy.orm as sql_orm_
import sqlalchemy.types as sql_t_
from app.core import getLogger, util
import _tables
import os
from sqlalchemy.schema import ForeignKey
import shutil
import time
from app.core.environment import Environment as env_
import traceback


log = getLogger(__name__)
class Database(object):
    """Provides a database abstraction"""
    typeLookup = {
         'i' :   sql_t_.Integer,
         's' :   sql_t_.Unicode,
         'b' :   sql_t_.Boolean,
         't' :   sql_t_.UnicodeText,
         'x' :   sql_t_.Binary,
    }
    """string identifiers to sqlalchemy column type translation dict"""

    def __init__(self, file):
        """Load sqlite database from file."""
        self.file = file
        self.engine = sql_.create_engine('sqlite:///%s' % file)
        self.metadata = sql_.schema.MetaData(self.engine)
        self.session = sql_orm_.scoped_session(
                sql_orm_.sessionmaker(bind = self.engine, autocommit = True)
        )

        env_._db = self
        log.info("Loading Database...")
        firstRun = not os.path.isfile(self.file)
        _tables.bootstrap(self)
        if firstRun:
            pass

    def createSession(self):
        """Create a new database session."""
        return self.session()

    def getTable(self, name, columns, constraints = None):
        constraints = constraints or [] #protected from persistent default argument
        columns = [self.getColumn(*args_ , **kwargs_) for args_, kwargs_ in columns]
        columns.extend(constraints)
        return sql_.schema.Table(
            name,
            self.metadata,
            *columns
        )

    def getAutoIdTable(self, name, columns, constraints = None):
        constraints = constraints or [] #protected from persistent default argument
        columns.insert(0, (('id', 'i'), {'primary_key' : True}))
        return self.getTable(
            name, columns
        )

    def getColumn(self, *args, **kwargs):
        """Construct a new `sqlalchema.schema.Column` based on list"""
        """
        Wrap Column class identifier and preprocess the
        input to add a few shorthand possibilities.
        
        1: column name
        
        2: column type
            can be of the following types:
            string:
                Translate a string identifier to valid sqlalchemy type
                    i: Integer
                    s: Unicode
                    b: Boolean
                    t: UnicodeText
                    x: Binary
            list:
                [type, args, kwargs} 
                Pass additional constructor arguments to the type.
                
                Type can also be a string which will be translated
                according to the aforementioned procedure.
            class:
                A valid sqlalchemy type
            instance:
                A valid sqlalchemy type instance
        
        3: Undocumented ForeignKey functionality.
        @todo: Explain the 3rd parameter
        """
        assert len(args) >= 2
        args = list(args) #copy to break link with original object

        #Perform described 2nd paramter magic
        type_list_default = [None, [], {}]

        #force list
        type_list = args[1] if isinstance(args[1], list) else [args[1]]

        #guarantee existence of *args and **kwargs
        type_list = util.list_apply_defaults(type_list, type_list_default)

        #string to type translation
        if isinstance(type_list[0], str):
            try:
                type_list[0] = Database.typeLookup[type_list[0]]
            except KeyError:
                log.error("Unsupported type identifier: %s" % type_list[0])

        args[1] = type_list[0](*type_list[1], **type_list[2])

        #foreign key handling
        if len(args) == 3:
            if isinstance(args[2], str):
                args[2] = ForeignKey(args[2])
            elif isinstance(args[2], tuple):
                args[2] = ForeignKey(args[2][0], **args[2][1])

        return sql_.schema.Column(
            *args,
            ** kwargs
        )

    def create(self):
        self.metadata.create_all()

    def getDbVersion(self):
        return env_.get('coreInfo')


    def upgradeDatabase(self, info, latest_version, scope):
        self.metadata.create_all()
        current_version = info.version
        session = self.createSession()
        if current_version < latest_version:
            log.info("Upgrading database for " + info.name)
            shutil.copy(self.file, self.file + '_' + time.strftime("%Y-%m-%d_%H-%M-%S") + '.db')
            for tempVersion in range(current_version + 1, latest_version + 1):
                methodName = 'migrateToVersion' + str(tempVersion)
                if hasattr(scope, methodName):
                    method = getattr(scope, methodName)
                    try:
                        method()
                        info.version += 1
                        session.add(info)
                        session.flush()
                    except:
                        log.info("Error while updating " + str(info.name) + ":\n" + traceback.format_exc())
                        return
                else:
                    log.info("Error while updating " + str(info.name)
                             + ": method " + methodName
                             + " not found.")
                    return
            #endfor
            log.info('Updated ' + str(info.name) + ', is now at version ' + str(info.version))
