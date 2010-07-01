from sqlalchemy import *
from sqlalchemy.orm import mapper, create_session
import datetime
import logging
import os

log = logging.getLogger(__name__)
path = os.path.abspath(os.path.curdir)

engine = create_engine('sqlite:///%s/data.db' % path)
metadata = MetaData(engine)
Session = create_session(bind = engine, autoflush = True)

movieTable = Table('Movie', metadata,
                     Column('id', Integer, primary_key = True),
                     Column('status', String()),
                     Column('dateAdded', DateTime(), default = datetime.datetime.utcnow),
                     Column('name', String()),
                     Column('year', Integer),
                     Column('imdb', String()),
                     Column('quality', String()),
                     Column('movieDb', String())
            )

historyTable = Table('History', metadata,
                     Column('id', Integer, primary_key = True),
                     Column('movieId', Integer, ForeignKey('Movie.id')),
                     Column('name', String())
            )

renameHistoryTable = Table('RenameHistory', metadata,
                     Column('id', Integer, primary_key = True),
                     Column('movieId', Integer, ForeignKey('Movie.id')),
                     Column('old', String()),
                     Column('new', String())
            )

class Movie(object):
    name = None

    def __init__(self):
        self.id = None

    def __repr__(self):
        return "<movie: %s" % self.name

movieMapper = mapper(Movie, movieTable)

class History(object):
    def __init__(self):
        self.id = None

    def __repr__(self):
        return "<history: %s" % self.name

historyMapper = mapper(History, historyTable)

class RenameHistory(object):
    def __init__(self):
        self.id = None

    def __repr__(self):
        return "<renamehistory: %s" % self.name

renameHistoryMapper = mapper(RenameHistory, renameHistoryTable)

def initDb():
    log.info('Initializing Database.')
    metadata.create_all()
    Session.close()
