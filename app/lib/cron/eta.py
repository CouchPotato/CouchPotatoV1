from app.config.cplog import CPLog
from app.config.db import Movie, MovieETA, Session as Db
from app.lib.cron.base import cronBase
from app.lib.provider.rss import rss
from dateutil.parser import parse
from sqlalchemy.sql.expression import or_
from urllib import urlencode
import Queue
import cherrypy
import time
import json

etaQueue = Queue.Queue()
log = CPLog(__name__)

class etaCron(rss, cronBase):

    apiUrl = 'http://couchpotatoapp.com/api/eta/%s/'

    def conf(self, option):
        return self.config.get('RottenTomatoes', option)

    def run(self):
        log.info('ETA thread is running.')

        timeout = 0.1 if self.debug else 1
        while True and not self.abort:

            try:
                queue = etaQueue.get(timeout = timeout)
                if queue.get('id'):
                    movie = Db.query(Movie).filter_by(id = queue.get('id')).first()
                else:
                    movie = queue.get('movie')

                if not cherrypy.config.get('debug'):
                    #do a search
                    self.running = True
                    result = self.search(movie)
                    if result:
                        self.save(movie, result)
                    self.running = False

                etaQueue.task_done()
                time.sleep(timeout)
            except Queue.Empty:
                pass

        log.info('ETA thread shutting down.')

    def all(self):
        activeMovies = Db.query(Movie).filter(or_(Movie.status == u'want', Movie.status == u'waiting')).all()
        for movie in activeMovies:
            etaQueue.put({'movie':movie})

    def save(self, movie, result):

        row = Db.query(MovieETA).filter_by(movieId = movie.id).first()
        if not row:
            row = MovieETA()
            Db.add(row)

        row.movieId = movie.id
        row.theater = result.get('theater')
        row.dvd = result.get('dvd')
        row.bluray = result.get('bluray')
        row.lastCheck = result.get('expires')
        Db.flush()

    def search(self, movie, page = 1):

        # Already found it, just update the stuff
        if movie.imdb:
            log.debug('Updating VideoETA for %s.' % movie.name)
            return self.getDetails(movie.imdb)

        log.info('No IMDBid available for ETA searching')

    def getDetails(self, id):

        url = self.apiUrl % id

        try:
            data = self.urlopen(url).read()
        except:
            log.error('Failed to open %s.' % url)
            return False

        try:
            dates = json.loads(data)
            log.info('Found ETA: %s' % dates)
        except:
            log.error('Error getting ETA for %s' % id)

        return dates


def startEtaCron(config, debug):
    c = etaCron()
    c.config = config
    c.debug = debug
    c.start()

    return c
