from app.core.db._tables import BasicTable
from sqlalchemy.orm import mapper

latestVersion = 0

class QueueTable(BasicTable):
    def __repr__(self):
        return BasicTable.__repr__(self) + self.name + str(self.version)


def bootstrap(db):

    # movie queue table
    columns = [
        [['movieId', 'i', 'core_movies_movie.id'], {}],
        [['quality', 'i', 'core_quality_quality.id'], {}],
        [['date', 'i'], {}],
        [['order', 'i'], {}],
        [['name', 's'], {}],
        [['link', 's'], {}],
        [['active', 'i'], {}],
        [['complete', 'i'], {}],
        [['wait_for', 'i'], {}],
        [['mark_complete', 'i'], {}],
        [['last_check', 'i'], {}],
        [['feeling_lucky', 'i'], {}],
        [['waitFor', 'i'], {}]
    ]
    queueTable = db.getAutoIdTable('core_queue', columns)
    mapper(QueueTable, queueTable)
