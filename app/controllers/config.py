from app.config.db import QualityTemplate, Session as Db
from app.controllers import BaseController
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

        if not data.get('Renamer.enabled'):
            data['Renamer.enabled'] = False
        if not data.get('global.launchbrowser'):
            data['global.launchbrowser'] = False
            
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
        self.cron.get('nzb').setInterval(config.get('Intervals', 'nzb'))

        # Writing our configuration file to 'example.cfg'
        config.save()

    @cherrypy.expose
    def exit(self):

        sys.exit()

    @cherrypy.expose
    @cherrypy.tools.mako(filename = "config/imdbScript.js")
    def imdbScript(self):
        '''
        imdb UserScript, for easy movie adding
        '''
        host = cherrypy.request.headers.get('host')
        #response.headers['content-type'] = 'text/javascript; charset=utf-8'
        return self.render({'host':host})

