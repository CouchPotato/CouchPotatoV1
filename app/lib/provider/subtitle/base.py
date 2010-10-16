from app.config.db import Session as Db, SubtitleHistory
from app.lib.provider.rss import rss
from sqlalchemy.sql.expression import and_

class subtitleBase(rss):

    def alreadyDownloaded(self, movie, file, key):
        key = self.getKey(key)
        movieId = 0 if not movie else movie.id

        results = Db.query(SubtitleHistory).filter(and_(SubtitleHistory.subtitle == key, SubtitleHistory.movie == movieId, SubtitleHistory.file == file)).all()

        for h in results:
            h.status = u'ignored'
            Db.flush()

        return len(results) > 0

    def addToHistory(self, movie, file, key, data):
        key = self.getKey(key)
        movieId = 0 if not movie else movie.id

        new = SubtitleHistory()
        new.movie = movieId
        new.file = file
        new.subtitle = key
        new.status = u'downloaded'
        new.data = str(data)
        Db.add(new)

        Db.flush()

    def getKey(self, key):
        return self.name + '-' + str(key)
