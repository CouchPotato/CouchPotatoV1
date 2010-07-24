from app.config.db import Session as Db, Movie, MovieETA
from app.controllers import BaseController, url, redirect
from sqlalchemy.sql.expression import or_
import cherrypy
import logging
import time

log = logging.getLogger(__name__)

class FeedController(BaseController):
    """ Search for new and cool movies and other stuff """

    @cherrypy.expose
    @cherrypy.tools.mako(filename = "feed/index.html")
    def index(self):

        # Releases
        theater = Db.query(MovieETA) \
            .filter(MovieETA.theater <= time.time() + 1814400) \
            .filter(MovieETA.theater >= time.time()) \
            .order_by(MovieETA.theater) \
            .all()
        dvd = Db.query(MovieETA) \
            .filter(MovieETA.dvd <= time.time() + 3628800) \
            .filter(MovieETA.dvd >= time.time()) \
            .order_by(MovieETA.dvd) \
            .all()

        dvdNow = Db.query(MovieETA) \
            .filter(MovieETA.dvd <= time.time()) \
            .filter(MovieETA.dvd > 0) \
            .order_by(MovieETA.dvd) \
            .all()

        return self.render({'dvd': dvd, 'theater':theater, 'dvdNow': dvdNow, 'running': self.cron.get('eta').isRunning()})

    def renewEta(self, **data):

        self.cron.get('eta').running = True
        activeMovies = Db.query(Movie).filter(or_(Movie.status == u'want', Movie.status == u'waiting')).all()
        for movie in activeMovies:
            self.searchers.get('etaQueue').put(movie)

        return redirect(url(controller = 'feed', action = 'index'))
