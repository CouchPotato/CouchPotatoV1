from app.lib.qualities import Qualities
from library.minify import Minify
import cherrypy
import routes

def url(*args, **kwargs):
    base = cherrypy.config.get('config').get('global', 'urlbase')
    base = '/' + base if base else 'http://'+cherrypy.request.headers.get('host')
    if len(args) == 1 and len(kwargs) == 0 and type(args[0]) in (str, unicode):
        return cherrypy.url(args[0], base = base)
    else:
        return cherrypy.url(routes.url_for(*args, **kwargs), base = base)

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
        self.globals['updater'] = cherrypy.config.get('updater')
        self.globals['searchers'] = self.searchers
        self.globals['cherrypy'] = cherrypy

    def updateGlobals(self):
        base = cherrypy.config.get('config').get('global', 'urlbase')

        if base:
            self.globals['baseUrl'] = 'http://'+cherrypy.request.headers.get('host') + '/' + base + '/'
        else:
            self.globals['baseUrl'] = 'http://'+cherrypy.request.headers.get('host') + '/'

        self.globals['lastCheck'] = self.cron.get('yarr').lastCheck()
        self.globals['nextCheck'] = self.cron.get('yarr').nextCheck()
        self.globals['checking'] = self.cron.get('yarr').isChecking()
        self.globals['stopped'] = self.cron.get('yarr').stop

    def render(self, list):

        self.updateGlobals()

        list.update(self.globals)

        return list
