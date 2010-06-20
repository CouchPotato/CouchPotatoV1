"""Movie model"""
from sqlalchemy import Column
from sqlalchemy.types import Integer, String, DateTime
import datetime

from moviemanager.model.meta import Base, Enum

class Movie(Base):
    __tablename__ = "Movie"

    id = Column(Integer, primary_key = True)
    status = Column(Enum([u'want', u'snatched', u'downloaded', u'deleted']))
    dateAdded = Column(DateTime(), default = datetime.datetime.utcnow);
    name = Column(String(100))
    year = Column(Integer)
    imdb = Column(String(20))
    quality = Column(String(20))
    movieDb = Column(Integer)

    #def __init__(self):

    def __repr__(self):
        return "%s" % self.name
