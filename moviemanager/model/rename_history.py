"""Person model"""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import relation, backref

from moviemanager.model.meta import Base

class RenameHistory(Base):
    __tablename__ = "RenameHistory"

    id = Column(Integer, primary_key=True)
    movieId = Column(Integer, ForeignKey('Movie.id'))
    old = Column(String(200))
    new = Column(String(200))
    
    movie = relation('Movie', backref=backref('History', order_by=id))


    def __init__(self, name=''):
        self.name = name

    def __repr__(self):
        return "<Movie('%s')" % self.name
