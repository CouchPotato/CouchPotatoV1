from app.core.db._tables import BasicTable
from sqlalchemy.orm import mapper

latestVersion = 0

class MovieTable(BasicTable):
    def __repr__(self):
        return BasicTable.__repr__(self) + self.name

def bootstrap(db):
    columns = [
        [['dateChanged', 'i'], {}],
        [['name', 's'], {}],
        [['status', 's'], {}],
        [['year', 'i'], {}],
        [['imdb', 's'], {}],
        [['movieDb', 's'], {}]
    ]
    movieTable = db.getAutoIdTable('core_movies_movie', columns)
    mapper(MovieTable, movieTable)
