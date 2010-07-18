from cherrypy.process.plugins import SimplePlugin
from imdb.parser.http.bsouplxml._bsoup import SoupStrainer, BeautifulSoup
from urllib2 import URLError
from zipfile import ZipFile
import cherrypy
import logging
import os
import tarfile
import urllib2

log = logging.getLogger(__name__)

class Updater(SimplePlugin):

    url = 'http://github.com/RuudBurger/CouchPotato/tarball/master'
    downloads = 'http://github.com/RuudBurger/CouchPotato/downloads'
    timeout = 10
    running = False

    def __init__(self, bus):
        SimplePlugin.__init__(self, bus)

    def start(self):
        self.basePath = cherrypy.config['basePath']
        self.runPath = cherrypy.config['runPath']
        self.cachePath = cherrypy.config['cachePath']
        self.updatePath = os.path.join(self.cachePath, 'updates')

    start.priority = 70

    def isRunning(self):
        return self.running

    def run(self):
        log.info("Updating")
        self.running = True
        if not os.path.isdir(self.updatePath):
            os.mkdir(self.updatePath)

        if os.name == 'nt':
            self.doUpdateWindows()
        else:
            self.doUpdateUnix()

        self.bus.restart()
        self.running = False

    def doUpdateWindows(self):
        try:
            data = urllib2.urlopen(self.downloads, timeout = self.timeout).read()
        except (IOError, URLError):
            log.error('Failed to open %s.' % self.downloads)
            return False

        try:
            tables = SoupStrainer('table')
            html = BeautifulSoup(data, parseOnlyThese = tables)
            resultTable = html.find('table', attrs = {'id':'s3_downloads'})

            latestUrl = 'http://github.com' + resultTable.find('a')['href'].replace(' ', '%20')
            try:
                latest = urllib2.urlopen(latestUrl, timeout = self.timeout)
            except (IOError, URLError):
                log.error('Failed to open %s.' % latestUrl)
                return False

            name = latest.geturl().split('/')[-1].replace('%20', ' ')
            destination = os.path.join(self.updatePath, name)

            if not os.path.isfile(destination):
                with open(destination, 'wb') as f:
                    f.write(latest.read())

            zip = ZipFile(destination)
            zip.extractall(path = self.updatePath)

            fromfile = os.path.join(self.updatePath, 'CouchPotato.exe')
            tofile = os.path.join(self.runPath, name.replace('.zip', '.exe'))
            os.rename(fromfile, tofile)

        except AttributeError:
            log.debug('Nothing found.')

    def doUpdateUnix(self):
        try:
            data = urllib2.urlopen(self.url, timeout = self.timeout)
        except (IOError, URLError):
            log.error('Failed to open %s.' % self.url)
            return False

        name = data.geturl().split('/')[-1]
        destination = os.path.join(self.updatePath, name)

        if not os.path.isfile(destination):
            # Remove older tarballs
            log.info('Removing old updates.')
            for file in os.listdir(self.updatePath):
                if os.path.isfile(file):
                    os.remove(file);
            
            log.info('Downloading %s.' % name)
            with open(destination, 'w') as f:
                f.write(data.read())

        log.info('Extracting.')
        tar = tarfile.open(destination)
        tar.extractall(path = self.updatePath)

        log.info('Moving updated files to CouchPotato root.')
        extractedPath = os.path.join(self.updatePath, name.replace('.tar.gz', ''))
        for root, subfiles, filenames in os.walk(extractedPath):
            for filename in filenames:
                fromfile = os.path.join(root, filename)
                tofile = os.path.join(self.runPath, fromfile.replace(extractedPath + os.path.sep, ''))
                try:
                    os.remove(tofile)
                except:
                    pass
                os.renames(fromfile, tofile)

        log.info('Update to %s successful.' % name)
