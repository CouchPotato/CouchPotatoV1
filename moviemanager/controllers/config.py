from moviemanager.lib.base import BaseController, render
from moviemanager.model.meta import Session as Db
from pylons import request, response, session, tmpl_context as c, url, config
from pylons.controllers.util import abort, redirect
from moviemanager.lib.quality import Quality
import logging
import time
import ConfigParser

cron = config.get('pylons.app_globals').cron
log = logging.getLogger(__name__)

class ConfigController(BaseController):
    """ Edit Config file"""

    def __before__(self):
        self.setGlobals()
        
        # Load config file
        c.configfile = config.get('__file__')
        c.parser = ConfigParser.RawConfigParser()
        c.parser.read(c.configfile)

    def index(self):
        '''
        Config form
        '''
        
        renamer = cron.get('renamer')
        replacements = {
             'cd': ' cd1',
             'cdNr': ' 1',
             'ext': 'mkv',
             'namethe': 'Big Lebowski, The',
             'thename': 'The Big Lebowski',
             'year': 1998,
             'first': 'B'
        }
        c.foldernameResult = renamer.doReplace(c.parser.get('Renamer', 'foldernaming'), replacements)
        c.filenameResult = renamer.doReplace(c.parser.get('Renamer', 'filenaming'), replacements)

        return render('/config/index.html')

    def save(self):
        '''
        Save all config settings
        '''
        
        # Save post data
        for name in request.params:
            section = name.split('.')[0]
            var = name.split('.')[1]
            c.parser.set(section, var, request.params[name])

        # Writing our configuration file to 'example.cfg'
        with open(c.configfile, 'wb') as configfile:
            c.parser.write(configfile)

        return redirect(url(controller = 'config', action = 'index'))
    
    def imdbScript(self):
        '''
        imdb UserScript, for easy movie adding
        '''
        c.host = request.host
        response.headers['content-type'] = 'text/javascript; charset=utf-8'
        return render('/config/imdbScript.js')


