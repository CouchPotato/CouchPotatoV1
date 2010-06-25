from moviemanager.lib.base import BaseController, render
from pylons import request, response, tmpl_context as c, url, config as conf
from pylons.controllers.util import redirect
import logging

cron = conf.get('pylons.app_globals').cron
config = conf.get('pylons.app_globals').config
log = logging.getLogger(__name__)

class ConfigController(BaseController):
    """ Edit Config file"""

    def __before__(self):
        self.setGlobals()

        c.trailerFormats = cron.get('trailer').formats

        # Load config file
        c.config = config

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
        c.foldernameResult = renamer.doReplace(c.config.get('Renamer', 'foldernaming'), replacements)
        c.filenameResult = renamer.doReplace(c.config.get('Renamer', 'filenaming'), replacements)

        return render('/config/index.html')

    def save(self):
        '''
        Save all config settings
        '''

        # Save post data
        for name in request.params:
            section = name.split('.')[0]
            var = name.split('.')[1]
            c.config.set(section, var, request.params[name])

        # Writing our configuration file to 'example.cfg'
        c.config.save()

        return redirect(url(controller = 'config', action = 'index'))

    def exit(self):

        exitrender = render('/config/exit.html')

        cron.get('quiter')()

        return exitrender

    def imdbScript(self):
        '''
        imdb UserScript, for easy movie adding
        '''
        c.host = request.host
        response.headers['content-type'] = 'text/javascript; charset=utf-8'
        return render('/config/imdbScript.js')


