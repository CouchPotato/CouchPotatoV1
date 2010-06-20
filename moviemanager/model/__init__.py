"""The application's model objects"""
from moviemanager.model.meta import Session, Base

from moviemanager.model.movie import Movie
from moviemanager.model.rename_history import RenameHistory
from moviemanager.model.feed import Feed

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind = engine)
