from app.config.db import QualityTemplate, Session as Db
from app.controllers import BaseController, redirect
from app.lib.qualities import Qualities
import cherrypy
import json
import logging
import sys

log = logging.getLogger(__name__)

class ConfigController(BaseController):

    @cherrypy.expose
    @cherrypy.tools.mako(filename = "config/index.html")
    def index(self):
        '''
        Config form
        '''
        config = cherrypy.config.get('config')

        renamer = self.cron.get('renamer')
        replacements = {
             'cd': ' cd1',
             'cdNr': ' 1',
             'ext': 'mkv',
             'namethe': 'Big Lebowski, The',
             'thename': 'The Big Lebowski',
             'year': 1998,
             'first': 'B'
        }

        trailerFormats = self.cron.get('trailer').formats
        foldernameResult = renamer.doReplace(config.get('Renamer', 'foldernaming'), replacements)
        filenameResult = renamer.doReplace(config.get('Renamer', 'filenaming'), replacements)

        return self.render({'trailerFormats':trailerFormats, 'foldernameResult':foldernameResult, 'filenameResult':filenameResult, 'config':config})

    @cherrypy.expose
    def save(self, **data):
        '''
        Save all config settings
        '''
        config = cherrypy.config.get('config')

        # catch checkboxes
        for bool in ['Renamer.enabled', 'Renamer.trailerQuality', 'Renamer.cleanup', 'global.launchbrowser', 'Torrents.enabled', 'NZB.enabled']:
            if not data.get(bool):
                data[bool] = False

        # Do quality order
        order = data.get('Quality.order').split(',')
        for id in order:
            qo = Db.query(QualityTemplate).filter_by(id = int(id)).one()
            qo.order = order.index(id)
            Db.flush()

        data['Quality.order'] = None

        # Save templates
        if data.get('Quality.templates'):
            templates = json.loads(data.get('Quality.templates'))
            Qualities().saveTemplates(templates)
        data['Quality.templates'] = None

        # Save post data
        for name in data:
            section = name.split('.')[0]
            var = name.split('.')[1]
            config.set(section, var, data[name])

        # Change cron interval
        self.cron.get('yarr').setInterval(config.get('Intervals', 'search'))

        config.save()

    @cherrypy.expose
    def exit(self):

        cherrypy.engine.exit()
        sys.exit()

    @cherrypy.expose
    def restart(self):

        cherrypy.engine.restart()

    @cherrypy.expose
    def update(self):

        updater = cherrypy.config.get('updater')
        result = updater.run()

        return 'Update successful, restarting...' if result else 'Update failed.'

    @cherrypy.expose
    def checkForUpdate(self):

        updater = cherrypy.config.get('updater')
        updater.checkForUpdate()

        return redirect(cherrypy.request.headers.get('referer'))

    @cherrypy.expose
    @cherrypy.tools.mako(filename = "config/userscript.js")
    def userscript(self):
        '''
        imdb UserScript, for easy movie adding
        '''
        host = cherrypy.request.headers.get('host')
        return self.render({'host':host})

