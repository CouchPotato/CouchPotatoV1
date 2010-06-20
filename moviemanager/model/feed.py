"""Feed model"""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.orm import relation, backref
import datetime

from moviemanager.model.meta import Base, Enum

class Feed(Base):
    __tablename__ = "Feed"

    id = Column(Integer, primary_key = True)
    movieId = Column(Integer, ForeignKey('Movie.id'))
    dateCached = Column(DateTime(), default = datetime.datetime.utcnow);
    
    name = Column(String(100))
    dateAdded = Column(DateTime(), default = datetime.datetime.utcnow);
    link = Column(String(200))
    contentId = Column(Integer)
    size = Column(Integer)
    
    score = Column(Integer)
    
    movie = relation('Movie', backref=backref('Feeds', lazy=False, order_by=score.desc()))

    def __repr__(self):
        return "%s" % self.name
