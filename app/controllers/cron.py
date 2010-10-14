from app.config.cplog import CPLog
from app.controllers import BaseController, redirect
import cherrypy

log = CPLog(__name__)

class CronController(BaseController):
    """ Do stuff to the cron. (sounds kinky!) """

    @cherrypy.expose
    def force(self):
        '''
        Force the cron to start
        '''

        self.cron.get('yarr').forceCheck()

        return redirect(cherrypy.request.headers.get('referer'))
    @cherrypy.expose
    def stop(self):

        self.cron.get('yarr').stopCheck()

        return redirect(cherrypy.request.headers.get('referer'))

    @cherrypy.expose
    def forceSingle(self, id):
        '''
        Force the cron for single movie
        '''

        #movie = Db.query(Movie).filter_by(id = id).one()
        self.cron.get('yarr').forceCheck(id)
        self.searchers.get('movie').getExtraInfo(id, overwrite = True)

    @cherrypy.expose
    def searchForTrailers(self):

        self.cron.get('trailer').searchExisting()

