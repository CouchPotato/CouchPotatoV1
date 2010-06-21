from moviemanager.lib.base import BaseController, render
from moviemanager.model.meta import Session as Db
from pylons import request, response, session, tmpl_context as c, url, config
from pylons.controllers.util import abort, redirect
from moviemanager.lib.quality import Quality
import logging
import time
import ConfigParser


log = logging.getLogger(__name__)

class ConfigController(BaseController):
    """ Edit Config file"""

    def __before__(self):
        self.setGlobals()
        
        # Load config file
        c.configfile = config.get('__file__')
        c.parser = ConfigParser.RawConfigParser()
        c.parser.read(c.configfile)

        self.initConfig()

    def index(self):
        '''
        Config form
        '''

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

    def initConfig(self):
        '''
        Create sections, in case the make-config didnt work properly
        '''

        if not c.parser.has_section('NZBsorg'):
            c.parser.add_section('NZBsorg')
            c.parser.set('NZBsorg', 'id', '')
            c.parser.set('NZBsorg', 'key', '')
            c.parser.set('NZBsorg', 'retention', '')

        if not c.parser.has_section('Sabnzbd'):
            c.parser.add_section('Sabnzbd')
            c.parser.set('Sabnzbd', 'host', '')
            c.parser.set('Sabnzbd', 'apikey', '')
            c.parser.set('Sabnzbd', 'username', '')
            c.parser.set('Sabnzbd', 'password', '')
            c.parser.set('Sabnzbd', 'category', '')

        if not c.parser.has_section('TheMovieDB'):
            c.parser.add_section('TheMovieDB')
            c.parser.set('TheMovieDB', 'key', '')

