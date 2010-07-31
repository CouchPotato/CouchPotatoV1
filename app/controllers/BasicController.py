class BaseController:
    globals = {
        'url': url,
        'Qualities': Qualities(),
        'Minify': Minify()
    }

    def __init__(self):
        self.cron = cherrypy.config.get('cron')
        self.searchers = cherrypy.config.get('searchers')
        self.flash = self.globals['flash'] = cherrypy.config.get('flash')
        self.globals['updater'] = cherrypy.config.get('updater')
        self.globals['searchers'] = self.searchers
        self.globals['cherrypy'] = cherrypy

    def updateGlobals(self):
        base = cherrypy.config.get('config').get('global', 'urlbase')
        host = 'http://' + cherrypy.request.headers.get('host') + '/'

        self.globals['baseUrl'] = host + base + '/' if base else host
        self.globals['yarr'] = self.cron.get('yarr')

    def render(self, list):

        self.updateGlobals()

        list.update(self.globals)

        return list
