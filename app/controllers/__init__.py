from app.lib.qualities import Qualities
from library.minify import Minify
import cherrypy
import routes

def url(*args, **kwargs):
    if len(args) == 1 and len(kwargs) == 0 and type(args[0]) in (str, unicode):
        return cherrypy.url(args[0])
    else:
        return cherrypy.url(routes.url_for(*args, **kwargs))

def redirect(url):
    raise cherrypy.HTTPRedirect(url)

class BaseController:

    globals = {
        'url': url,
        'Qualities': Qualities(),
        'Minify': Minify()
    }

    def __init__(self):
        self.cron = cherrypy.config.get('cron')
        self.searchers = cherrypy.config.get('searchers')
        self.globals['debug'] = cherrypy.config.get('debug')
        
    def updateGlobals(self):

        self.globals['lastCheck'] = self.cron.get('nzb').lastCheck()
        self.globals['nextCheck'] = self.cron.get('nzb').nextCheck()
        self.globals['checking'] = self.cron.get('nzb').isChecking()

    def render(self, list):
        
        self.updateGlobals()

        list.update(self.globals)

        return list
