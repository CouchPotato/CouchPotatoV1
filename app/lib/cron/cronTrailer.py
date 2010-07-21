from app.lib.cron.cronBase import cronBase
from app.lib.provider.rss import rss
from app.lib.provider.trailers.hdtrailers import HdTrailers
from app.lib.provider.trailers.youtube import Youtube
from urllib2 import URLError
import Queue
import cherrypy
import hashlib
import logging
import os
import shutil
import urllib2

trailerQueue = Queue.Queue()
log = logging.getLogger(__name__)

class TrailerCron(rss, cronBase):

    formats = ['1080p', '720p', '480p']
    sources = []
    config = None

    def run(self):
        log.info('TrailerCron thread is running.')

        self.tempdir = cherrypy.config.get('cachePath')

        # Sources
        self.sources.append(HdTrailers(self.config))
        self.sources.append(Youtube(self.config))

        timeout = 0.1 if self.debug else 1
        while True and not self.abort:
            try:
                movie = trailerQueue.get(timeout = timeout)

                #do a search
                self.running = True
                self.search(movie['movie'], movie['destination'])
                self.running = False

                trailerQueue.task_done()
            except Queue.Empty:
                pass


        log.info('TrailerCron shutting down.')

    def search(self, movie, destination):

        if self.config.get('Trailer', 'name') != 'movie-trailer':
            trailerFinal = 'movie-trailer'
        else:
            trailerFinal = os.path.splitext(destination.get('filename'))[0]
            trailerFinal = trailerFinal[:len(trailerFinal) - 1] + '-trailer'

        trailerFinal = os.path.join(destination.get('directory'), trailerFinal)

        for source in self.sources:
            results = source.find(movie)
            for quality, items in results.iteritems():
                if quality == self.config.get('Trailer', 'quality'):
                    items.reverse()
                    for result in items:
                        trailer = self.download(result)
                        if trailer:
                            log.info('Trailer found for %s.' % movie.name)
                            shutil.move(trailer, trailerFinal + os.path.splitext(trailer)[1])
                            return True

        log.info('No trailer found for %s.' % movie.name)

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
            f.write(data.read())

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
