import ConfigParser
import logging
import os
import shutil

log = logging.getLogger(__name__)

class configApp():

    s = ['Sabnzbd', 'TheMovieDB', 'NZBsorg', 'Renamer', 'IMDB', 'Intervals']

    def __init__(self, file):
        self.file = file

        self.p = ConfigParser.RawConfigParser()
        self.p.read(file)

        self.initConfig()

    def parser(self):
        return self.p

    def sections(self):
        return self.s

    def set(self, section, option, value):
        return self.p.set(section, option, value)

    def get(self, section, option):
        return self.p.get(section, option)

    def initConfig(self):
        '''
        Create sections, in case the make-config didnt work properly
        '''

        self.addSection('global')
        self.setDefault('global', 'server.environment', 'production')
        self.setDefault('global', 'engine.autoreload_on', 'False')
        self.setDefault('global', 'host', '0.0.0.0')
        self.setDefault('global', 'port', 5000)
        self.setDefault('global', 'username', '')
        self.setDefault('global', 'password', '')
        self.setDefault('global', 'launchbrowser', 'True')

        self.addSection('Renamer')
        self.setDefault('Renamer', 'enabled', 'False')
        self.setDefault('Renamer', 'download', '')
        self.setDefault('Renamer', 'destination', '')
        self.setDefault('Renamer', 'folderNaming', '<namethe> (<year>)')
        self.setDefault('Renamer', 'fileNaming', '<thename><cd>.<ext>')
        self.setDefault('Renamer', 'trailerQuality', 'False')

        self.addSection('NZBsorg')
        self.setDefault('NZBsorg', 'id', '')
        self.setDefault('NZBsorg', 'key', '')
        
        self.addSection('NZB')
        self.setDefault('NZB', 'retention', 300)
        self.setDefault('NZB', 'sendTo', 'Sabnzbd')
        self.setDefault('NZB', 'blackhole', '')

        self.addSection('Sabnzbd')
        self.setDefault('Sabnzbd', 'host', 'localhost:8080')
        self.setDefault('Sabnzbd', 'apikey', '')
        self.setDefault('Sabnzbd', 'username', '')
        self.setDefault('Sabnzbd', 'password', '')
        self.setDefault('Sabnzbd', 'category', '')

        self.addSection('TheMovieDB')
        self.setDefault('TheMovieDB', 'key', '9b939aee0aaafc12a65bf448e4af9543')

        self.addSection('IMDB')

        self.addSection('Intervals')
        self.setDefault('Intervals', 'nzb', '24')
        self.setDefault('Intervals', 'renamer', '5')

        self.addSection('Quality')
        self.setDefault('Quality', 'hide', 'cam')
        self.setDefault('Quality', 'default', '720p')

        self.save()

    def save(self):
        with open(self.file, 'wb') as configfile:
            self.p.write(configfile)

    def addSection(self, section):
        if not self.p.has_section(section):
            self.p.add_section(section)

    def setDefault(self, section, option, value):
        if not self.p.has_option(section, option):
            self.p.set(section, option, value)

class Auth():

    def __init__(self, username, password):
        self.u = username
        self.p = password

    def test(self, environ, username, password):
        if username == self.u and password == self.p:
            return True
        else:
            return False
