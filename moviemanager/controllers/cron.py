from moviemanager.lib.base import BaseController
from moviemanager.model import Movie
from moviemanager.model.meta import Session as Db
from pylons import request, config
from pylons.controllers.util import redirect
import logging

cron = config.get('pylons.app_globals').cron
log = logging.getLogger(__name__)

class CronController(BaseController):
    """ Do stuff to the cron. (sounds kinky!) """

    def __before__(self):
        self.qMovie = Db.query(Movie)

    def force(self):
        '''
        Force the cron to start
        '''

        cron.get('nzb').forceCheck()

        return redirect(request.headers.get('REFERER', '/'))

    def forceSingle(self, id):
        '''
        Force the cron for single movie
        '''

        movie = self.qMovie.filter_by(id = id).one()
        cron.get('nzb').forceCheck(movie)

        return redirect(request.headers.get('REFERER', '/'))
