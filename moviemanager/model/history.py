"""History model"""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import relation, backref

from moviemanager.model.meta import Base, Enum

class History(Base):
    __tablename__ = "History"

    id = Column(Integer, primary_key=True)
    movieId = Column(Integer, ForeignKey('Movie.id'))
    name = Column(String(200))
    
    movie = relation('Movie', backref=backref('History'))


    def __init__(self, name=''):
        self.name = name
