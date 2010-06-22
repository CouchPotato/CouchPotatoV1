
from moviemanager.model import Movie, Feed
from moviemanager.model.meta import Session as Db
import Queue
import logging
import threading
import time

log = logging.getLogger(__name__)

NzbCronQueue = Queue.Queue()
class NzbCron(threading.Thread):

    ''' Cronjob for searching for NZBs '''

    lastChecked = 0
    interval = 60 #minutes
    provider = None
    sabNzbd = None
    intervalSec = 10
    checking = False
    checkTheseMovies = []

    def run(self):
        log.info('NzbCron thread is running.')

        self.intervalSec = (self.interval * 60)
        self.forceCheck()
        time.sleep(10)

        while True:

            #check single movie
            for movie in self.checkTheseMovies:
                self._searchNzb(movie)
                self.checkTheseMovies.pop(0)
                log.info('Sleeping search for 5 sec')
                time.sleep(5)

            #check all movies
            now = time.time()
            if (self.lastChecked + self.intervalSec) < now:
                self.lastChecked = now
                self.searchNzbs()

            #log.info('Sleeping NzbCron for %d seconds' % 10)
            time.sleep(10)

    def forceCheck(self, movie = None):
        if movie == None:
            self.lastChecked = time.time() - self.intervalSec + 10
        else:
            self.checkTheseMovies.append(movie)

    def searchNzbs(self):
        log.info('Searching for NZB.')
        self.doCheck()

        #get al wanted movies
        movies = Db.query(Movie).filter_by(status = u'want')

        for movie in movies:
            self._searchNzb(movie)

            log.info('Sleeping search for 5 sec')
            time.sleep(5)

        self.doCheck(False)
        log.info('Finished search.')


    def _searchNzb(self, movie):

        results = self.provider.find(movie)

        #search for highest score
        highest = None
        highestScore = 0
        for result in results:
            if result.score > highestScore:
                highest = result

        #send highest to SABnzbd & mark as snatched
        if highest:
            success = self.sabNzbd.send(highest)


    def doCheck(self, bool = True):
        self.checking = bool
        self.lastChecked = time.time()

    def isChecking(self):
        return self.checking

    def lastCheck(self):
        return self.lastChecked

    def nextCheck(self):

        t = (self.lastChecked + self.intervalSec) - time.time()

        if t >= 60:
            mins = int(t / 60)
            rsecs = t % 60
        else:
            mins = 0
            rsecs = t

        s = "%.2f minutes" % (mins + rsecs / 100.0)

        return {
            'timestamp': t,
            'string': s
        }

def startNzbCron():
    cron = NzbCron()
    cron.start()

    return cron
