from app.lib.cron.cronBase import cronBase
from app.lib.provider.rss import rss
from app.lib.provider.trailers.hdtrailers import HdTrailers
from app.lib.provider.trailers.youtube import Youtube
from urllib2 import URLError
import Queue
import cherrypy
import fnmatch
import hashlib
import logging
import os
import re
import shutil
import time
import urllib2

trailerQueue = Queue.Queue()
log = logging.getLogger(__name__)

class TrailerCron(rss, cronBase):

    formats = ['1080p', '720p', '480p']
    sources = []
    config = None
    searchingExisting = 0

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

    def searchExisting(self):
        
        if not self.searchingExisting < time.time()-300:
            log.info('Just searched for trailers. Can do a search every 5 minutes.')
            return
        
        if not self.config.get('Trailer', 'quality') or not self.config.get('Renamer', 'destination'):
            log.info('No trailer quality set or no movie folder found.')
            return

        log.info('Searching for trailers for existing movies.')
        self.searchingExisting = time.time()

        movieFolder = self.config.get('Renamer', 'destination')
        movieList = []
        for root, subfiles, filenames in os.walk(movieFolder):
            log.debug(subfiles)
            for file in filenames:
                fullPath = os.path.join(root, file)
                if not '-trailer' in file.lower() and os.path.getsize(fullPath) > (400 * 1024 * 1024):
                    hasTrailer = False
                    nfo = None
                    for checkfile in filenames:
                        if '-trailer' in checkfile.lower():
                            hasTrailer = True
                        if '.nfo' in checkfile.lower():
                            nfo = checkfile

                    if not hasTrailer:
                        movieList.append({
                            'directory': root,
                            'filename': file,
                            'nfo': nfo
                        })

        for movieFiles in movieList:
            movie = None
            nfo = None
            year = None
            
            if self.abort:
                break

            if movieFiles.get('nfo'):
                nfoFile = os.path.join(movieFiles.get('directory'), movieFiles.get('nfo'))
                handle = open(nfoFile, 'r')
                nfo = self.getItems(handle, '')
                handle.close()

            # Get name via nfo
            if nfo:
                imdb = self.gettextelement(nfo[0], 'id')
                if imdb:
                    movie = cherrypy.config.get('searchers').get('movie').findByImdbId(imdb)
            else:
                q = self.toSearchString(os.path.splitext(movieFiles.get('filename'))[0])

                year = self.findYear(movieFiles.get('filename'))
                year = year if year else self.findYear(movieFiles.get('directory'))

                if q and year:
                    guess = cherrypy.config.get('searchers').get('movie').find(q + ' ' + year, limit = 1, alternative = False)
                    if guess:
                        movie = guess.pop()

            if movie:
                trailerQueue.put({'id': movie.imdb, 'movie': movie, 'destination':movieFiles})
            else:
                log.info('No match found for: %s' % movieFiles.get('filename'))

            time.sleep(2)

    def findYear(self, text):
        matches = re.search('(?P<year>[0-9]{4})', text)
        if matches:
            return matches.group('year')

        return None

    def search(self, movie, destination):

        if self.config.get('Trailer', 'name') != 'movie-trailer':
            trailerFinal = 'movie-trailer'
        else:
            trailerFinal = os.path.splitext(destination.get('filename'))[0]
            trailerFinal = trailerFinal[:len(trailerFinal) - 1] + '-trailer'

        trailerFinal = os.path.join(destination.get('directory'), trailerFinal)

        for source in self.sources:
            results = source.find(movie)
            if results:
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
        time.sleep(2)

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

        if self.debug:
            return

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
