from app.config.db import Session as Db, Movie, MovieETA
from app.controllers import BaseController, url, redirect
import cherrypy
import logging
import time

log = logging.getLogger(__name__)

class FeedController(BaseController):
    """ Search for new and cool movies and other stuff """

    @cherrypy.expose
    @cherrypy.tools.mako(filename = "feed/index.html")
    def index(self):

        range = 3628800 #seconds

        # Releases
        theater = Db.query(MovieETA) \
            .filter(MovieETA.theater <= time.time() + range) \
            .filter(MovieETA.theater >= time.time()) \
            .order_by(MovieETA.theater) \
            .all()
        dvd = Db.query(MovieETA) \
            .filter(MovieETA.dvd <= time.time() + range) \
            .filter(MovieETA.dvd >= time.time()) \
            .order_by(MovieETA.dvd) \
            .all()

        return self.render({'dvd': dvd, 'theater':theater, 'running': self.cron.get('eta').isRunning()})

    def renewEta(self, **data):

        all = data.get('all')

        for movie in Db.query(Movie).all():
            if not movie.eta or all:
                self.searchers.get('etaQueue').put(movie)

        return redirect(url(controller = 'feed', action = 'index'))
