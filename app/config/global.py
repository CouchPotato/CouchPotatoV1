import ConfigParser
import logging
from app.config.wrapper import Wrapper

log = logging.getLogger(__name__)

class App(Wrapper):

    s = ['Sabnzbd', 'TheMovieDB', 'NZBsorg', 'Renamer', 'IMDB', 'Intervals']
    bool = {'true':True, 'false':False}

    def __init__(self, path):
        Wrapper.__init__(self, path)

    def parser(self):
        return self.p

    def sections(self):
        return self.s

    def set(self, section, option, value):
        return self.p.set(section, option, value)

    def get(self, section, option):
        value = self.p.get(section, option)
        if str(value).lower() in self.bool:
            return self.bool.get(str(value).lower())
        return value

    def initConfig(self):
        '''
        Create sections, in case the make-config didnt work properly
        '''

        self.addSection('global')
        self.setDefault('global', 'server.environment', 'production')
        self.setDefault('global', 'engine.autoreload_on', False)
        self.setDefault('global', 'host', '0.0.0.0')
        self.setDefault('global', 'port', 5000)
        self.setDefault('global', 'username', '')
        self.setDefault('global', 'password', '')
        self.setDefault('global', 'launchbrowser', True)
        self.setDefault('global', 'urlBase', '')
        self.setDefault('global', 'feelingLucky', False) #choose release automatically?

        self.addSection('Renamer')
        self.setDefault('Renamer', 'enabled', False)
        self.setDefault('Renamer', 'download', '')
        self.setDefault('Renamer', 'destination', '')
        self.setDefault('Renamer', 'folderNaming', '<namethe> (<year>)')
        self.setDefault('Renamer', 'fileNaming', '<thename><cd>.<ext>')
        self.setDefault('Renamer', 'cleanup', False)

        self.addSection('Trailer')
        self.setDefault('Trailer', 'quality', False)
        self.setDefault('Trailer', 'name', 'movie-trailer')

        self.addSection('NZBsorg')
        self.setDefault('NZBsorg', 'id', '')
        self.setDefault('NZBsorg', 'key', '')
        self.addSection('NZBMatrix')
        self.setDefault('NZBMatrix', 'username', '')
        self.setDefault('NZBMatrix', 'apikey', '')

        self.addSection('NZB')
        self.setDefault('NZB', 'enabled', True)
        self.setDefault('NZB', 'retention', 300)
        self.setDefault('NZB', 'sendTo', 'Sabnzbd')
        self.setDefault('NZB', 'blackhole', '')

        self.addSection('Torrents')
        self.setDefault('Torrents', 'enabled', False)
        self.setDefault('Torrents', 'wait', 24)
        self.setDefault('Torrents', 'blackhole', '')

        self.addSection('Sabnzbd')
        self.setDefault('Sabnzbd', 'host', 'localhost:8080')
        self.setDefault('Sabnzbd', 'apikey', '')
        self.setDefault('Sabnzbd', 'username', '')
        self.setDefault('Sabnzbd', 'password', '')
        self.setDefault('Sabnzbd', 'category', '')

        self.addSection('Intervals')
        self.setDefault('Intervals', 'search', '24')
        self.setDefault('Intervals', 'renamer', '5')

        self.addSection('Quality')
        self.setDefault('Quality', 'hide', 'cam')
        self.setDefault('Quality', 'default', '720p')

        self.addSection('paths')
        self.setDefault('paths', 'cache', 'cache')
        self.setDefault('paths', 'database', 'data.db')
        self.setDefault('paths', 'logs', 'logs')

        self.save()

class Auth():

    def __init__(self, username, password):
        self.u = username
        self.p = password

    def test(self, environ, username, password):
        if username == self.u and password == self.p:
            return True
        else:
            return False
