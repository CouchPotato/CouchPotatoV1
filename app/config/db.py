from sqlalchemy import *
from sqlalchemy.orm import mapper, create_session
import datetime

# Inform SQLAlchemy of the database we will use
# A SQLlite 'in memory' database
# Mapped into an engine object and bound to a high
# level meta data interface
engine = create_engine('sqlite:///data.db')
metadata = MetaData(engine)
Session = create_session(bind=engine)

movieTable = Table('Movie', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('status', String()),
                     Column('dateAdded', DateTime(), default = datetime.datetime.utcnow),
                     Column('name', String()),
                     Column('year', Integer),
                     Column('imdb', String()),
                     Column('quality', String()),
                     Column('movieDb', String())
            )
movieTable.create(checkfirst=True)

historyTable = Table('History', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('movieId', Integer, ForeignKey('Movie.id')),
                     Column('name', String())
            )
historyTable.create(checkfirst=True)

renameHistoryTable = Table('RenameHistory', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('movieId', Integer, ForeignKey('Movie.id')),
                     Column('old', String()),
                     Column('new', String())
            )
renameHistoryTable.create(checkfirst=True)





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



#    id = Column(Integer, primary_key = True)
#    status = Column(Enum([u'want', u'snatched', u'downloaded', u'deleted']))
#    dateAdded = Column(DateTime(), default = datetime.datetime.utcnow);
#    name = Column(String(100))
#    year = Column(Integer)
#    imdb = Column(String(20))
#    quality = Column(String(20))
#    movieDb = Column(Integer)
#
#song_table = Table('Song', metadata,
#                   Column('id', Integer, primary_key=True),
#                   Column('title', String()),
#                   Column('position', Integer),
#                   Column('album_id', Integer,
#                          ForeignKey('Album.id')))
#
#album_table = Table('Album', metadata,
#                    Column('id', Integer, primary_key=True),
#                    Column('title', String()),
#                    Column('release_year', Integer),
#                    Column('artist_id', Integer,
#                           ForeignKey('Artist.id')))


#class Album(object):
#    def __init__(self, title, release_year=0):
#        self.id = None
#        self.title = title
#        self.release_year = release_year
#
#class Song(object):
#    def __init__(self, title, position=0):
#        self.id = None
#        self.title = title
#        self.position = position

#song_mapper = mapper(Song, song_table)
#album_mapper = mapper(Album, album_table,
#                      properties = {'songs': relation(song_mapper,
#                                    cascade="all, delete-orphan")
#                                   })
#artist_mapper = mapper(Artist, artist_table,
#                       properties = {'albums': relation(album_mapper,
#                                     cascade="all, delete-orphan")
#                                    }) 