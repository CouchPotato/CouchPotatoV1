import ConfigParser

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

        self.addSection('Renamer')
        self.setDefault('Renamer', 'enabled', 'false')
        self.setDefault('Renamer', 'download', '')
        self.setDefault('Renamer', 'destination', '')
        self.setDefault('Renamer', 'folderNaming', '<namethe> (<year>)')
        self.setDefault('Renamer', 'fileNaming', '<thename><cd>.<ext>')
        self.setDefault('Renamer', 'trailerQuality', 'false')

        self.addSection('NZBsorg')
        self.setDefault('NZBsorg', 'id', '')
        self.setDefault('NZBsorg', 'key', '')
        self.setDefault('NZBsorg', 'retention', '')

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
