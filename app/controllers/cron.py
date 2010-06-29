from app.config.db import Session as Db, Movie
from app.controllers import BaseController, url, redirect
import cherrypy
import logging

log = logging.getLogger(__name__)
qMovie = Db.query(Movie)

class CronController(BaseController):
    """ Do stuff to the cron. (sounds kinky!) """

    @cherrypy.expose
    def force(self):
        '''
        Force the cron to start
        '''

        self.cron.get('nzb').forceCheck()

        return redirect(cherrypy.request.headers.get('referer'))

    @cherrypy.expose
    def forceSingle(self, id):
        '''
        Force the cron for single movie
        '''

        movie = qMovie.filter_by(id = id).one()
        self.cron.get('nzb').forceCheck(movie)

        return redirect(cherrypy.request.headers.get('referer'))

