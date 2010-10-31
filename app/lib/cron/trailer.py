from app.config.cplog import CPLog
from app.config.db import Session as Db, Movie
from app.lib import library
from app.lib.cron.base import cronBase
from app.lib.library import Library
from app.lib.provider.rss import rss
from app.lib.provider.trailers.hdtrailers import HdTrailers
from urllib2 import URLError
import Queue
import cherrypy
import hashlib
import os
import re
import shutil
import time
import urllib2

trailerQueue = Queue.Queue()
log = CPLog(__name__)

class TrailerCron(rss, cronBase, Library):

    formats = ['1080p', '720p', '480p']
    providers = []
    config = None
    searchingExisting = 0

    def run(self):
        log.info('TrailerCron thread is running.')

        self.tempdir = cherrypy.config.get('cachePath')

        # Provider
        for provider in [HdTrailers]:
            p = provider(self.config)
            self.providers.append(p)

        timeout = 0.1 if self.debug else 1
        while True and not self.abort:
            try:
                movie = trailerQueue.get(timeout = timeout)

                #do a search
                self.running = True
                self.search(movie)
                self.running = False

                trailerQueue.task_done()
            except Queue.Empty:
                pass

        log.info('TrailerCron shutting down.')

    def conf(self, value):
        return self.config.get('Trailer', value)

    def isEnabled(self):
        return self.conf('quality')

    def forDirectory(self, directory):
        log.info('Finding trailers for: %s' % directory)
        self.searchExisting(directory, force = True)

    def searchExisting(self, directory = None, force = False):

        if not self.searchingExisting < time.time() - 300 and not self.debug:
            log.info('Just searched for trailers. Can do a search every 5 minutes.')
            return
        elif not self.isEnabled():
            return

        if not directory: log.info('Adding movies to trailer search.')
        self.searchingExisting = time.time()
        movies = self.getMovies(directory)

        for movie in movies:
            if not movie.get('trailer') or force:
                trailerQueue.put(movie)

        if not directory: log.info('Done adding movies to trailer search.')

    def search(self, movie):
        log.info('Search for trailer for: %s' % movie['folder'])

        if self.abort:
            return

        if self.conf('name') == 'movie-trailer':
            trailerFinal = 'movie-trailer'
        else:
            trailerFinal = movie['filename'] + '-trailer'

        trailerFinal = os.path.join(movie['path'], trailerFinal)

        # Rename existing trailer
        if movie['trailer']:
            addNumber = len(movie['trailer']) > 1
            i = 1
            for trailer in movie['trailer']:
                oldName = os.path.join(movie['path'], trailer['filename'])
                newName = trailerFinal if not addNumber else trailerFinal + str(i)
                shutil.move(oldName, newName + '.' + trailer['ext'])
                i += 1
            return True

        if not movie['movie']:
            log.info("Unknown movie: '%s'." % movie['folder'])
            return

        for provider in self.providers:
            results = provider.find(movie['movie'])
            if results:
                for quality, items in results.iteritems():
                    if quality == self.conf('quality'):
                        for result in items:
                            trailer = self.download(result)
                            if trailer:
                                shutil.move(trailer, trailerFinal + os.path.splitext(trailer)[1])
                                return True

        log.debug('No trailer found for %s.' % movie['folder'])

    def download(self, url):
        try:
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Quicktime') # Love you apple!
            data = urllib2.urlopen(req, timeout = self.timeout)
        except (IOError, URLError):
            log.error('Failed to open %s.' % url)
            return False

        ext = self.extention(data.geturl())
        hash = hashlib.md5(url).hexdigest()

        tempTrailerFile = os.path.join(self.tempdir, hash + ext)

        # Remove the old
        if os.path.isfile(tempTrailerFile):
            os.remove(tempTrailerFile)

        log.info('Downloading trailer "%s", %d MB' % (url, int(data.info().getheaders("Content-Length")[0]) / 1024 / 1024))

        with open(tempTrailerFile, 'wb') as f:
            f.write(data.read() if not self.debug else 'trailer')

        log.info('Download of %s finished.' % url)

        return tempTrailerFile

    def extention(self, url):
        return '.mov' if '.mov' in url else '.mp4'

def startTrailerCron(config, debug):
    cron = TrailerCron()
    cron.config = config
    cron.debug = debug
    cron.start()

    return cron
