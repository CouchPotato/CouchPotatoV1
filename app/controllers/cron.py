from app.config.cplog import CPLog
from app.controllers import BaseController, redirect
import cherrypy

log = CPLog(__name__)

class CronController(BaseController):
    """ Do stuff to the cron. (sounds kinky!) """

    @cherrypy.expose
    def force(self):
        self.cron.get('yarr').forceCheck()
        return redirect(cherrypy.request.headers.get('referer'))
    @cherrypy.expose
    def stop(self):
        self.cron.get('yarr').stopCheck()
        return redirect(cherrypy.request.headers.get('referer'))

    @cherrypy.expose
    def forceSingle(self, id):
        self.cron.get('yarr').forceCheck(id)
        self.searchers.get('movie').getExtraInfo(id, overwrite = True)

    @cherrypy.expose
    def searchForTrailers(self):
        self.cron.get('trailer').searchExisting()

    @cherrypy.expose
    def searchForSubtitles(self):
        self.cron.get('subtitle').searchExisting()
