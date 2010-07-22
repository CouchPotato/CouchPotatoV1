from app import version
from cherrypy.process.plugins import SimplePlugin
from imdb.parser.http.bsouplxml._bsoup import SoupStrainer, BeautifulSoup
from urllib2 import URLError
import cherrypy
import logging
import os
import tarfile
import time
import urllib2

log = logging.getLogger(__name__)

class Updater(SimplePlugin):

    url = 'http://github.com/RuudBurger/CouchPotato/tarball/master'
    downloads = 'http://github.com/RuudBurger/CouchPotato/downloads'
    timeout = 10
    running = False
    version = None
    updateAvailable = False
    availableString = None
    lastCheck = 0

    def __init__(self, bus):
        SimplePlugin.__init__(self, bus)

    def start(self):
        self.basePath = cherrypy.config['basePath']
        self.runPath = cherrypy.config['runPath']
        self.cachePath = cherrypy.config['cachePath']
        self.isFrozen = cherrypy.config['frozen']
        self.debug = cherrypy.config['debug']
        self.updatePath = os.path.join(self.cachePath, 'updates')
        self.historyFile = os.path.join(self.updatePath, 'history.txt')

        if not os.path.isdir(self.updatePath):
            os.mkdir(self.updatePath)

        if not os.path.isfile(self.historyFile):
            self.history('UNKNOWN Build.')

        self.checkForUpdate()
        self.getVersion()

    start.priority = 70

    def isRunning(self):
        return self.running

    def run(self):

        if self.isFrozen:
            return self.checkForUpdateWindows()
        else:
            log.info("Updating")
            self.running = True

            result = self.doUpdateUnix()
            self.bus.restart()
            
            self.running = False
            return result

    def getVersion(self, force = False):

        if not self.version or force:
            if self.isFrozen:
                self.version = 'Windows build r%d' % version.windows
            else:
                handle = open(self.historyFile, "r")
                lineList = handle.readlines()
                handle.close()
                self.version = lineList[-1].replace('RuudBurger-CouchPotato-', '').replace('.tar.gz', '')

        return self.version

    def checkForUpdate(self):

        if self.debug:
            return

        if self.isFrozen:
            self.updateAvailable = self.checkForUpdateWindows()
        else:
            update = self.checkForUpdateUnix()
            history = open(self.historyFile, 'r').read()
            self.updateAvailable = update.get('name').replace('.tar.gz', '') not in history

        self.availableString = 'Update available' if self.updateAvailable else 'No update available'
        self.lastCheck = time.time()
        log.info(self.availableString)

    def checkForUpdateUnix(self):
        try:
            data = urllib2.urlopen(self.url, timeout = self.timeout)
        except (IOError, URLError):
            log.error('Failed to open %s.' % self.url)
            return False

        name = data.geturl().split('/')[-1]
        return {'name':name, 'data':data}


    def checkForUpdateWindows(self):
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

            downloadUrl = latest.geturl()

            if 'r' + str(version.windows) in downloadUrl:
                return False

            return downloadUrl

        except AttributeError:
            log.debug('Nothing found.')

        return False

    def doUpdateUnix(self):
        update = self.checkForUpdateUnix()
        if not update:
            return False

        name = update.get('name')
        data = update.get('data')
        destination = os.path.join(self.updatePath, update.get('name'))

        if not os.path.isfile(destination):
            # Remove older tarballs
            log.info('Removing old updates.')
            for file in os.listdir(self.updatePath):
                filename = os.path.join(self.updatePath, file)
                if os.path.isfile(filename) and not '.txt' in filename:
                    os.remove(filename);

            log.info('Downloading %s.' % name)
            with open(destination, 'w') as f:
                f.write(data.read())

        log.info('Extracting.')
        tar = tarfile.open(destination)
        tar.extractall(path = self.updatePath)

        log.info('Moving updated files to CouchPotato root.')
        name = name.replace('.tar.gz', '')
        extractedPath = os.path.join(self.updatePath, name)
        for root, subfiles, filenames in os.walk(extractedPath):
            for filename in filenames:
                fromfile = os.path.join(root, filename)
                tofile = os.path.join(self.runPath, fromfile.replace(extractedPath + os.path.sep, ''))

                if not self.debug:
                    try:
                        os.remove(tofile)
                    except:
                        pass
                    os.renames(fromfile, tofile)

        self.history(name)
        log.info('Update to %s successful.' % name)
        return True

    def history(self, version):
        handle = open(self.historyFile, "a")
        handle.write(version + "\n")
        handle.close()
